import logging
from struct import pack
import re
import base64
import asyncio
import time as _time
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from marshmallow.exceptions import ValidationError
from database.client import db
from info import COLLECTION_NAME, USE_CAPTION_FILTER, MAX_B_TN, FILTER_WORDS
from utils import get_settings, save_group_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


instance = Instance.from_db(db)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME


async def save_file(media):
    """Save file in database"""

    # TODO: Find better way to get same file_id for same media to avoid duplicates
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    try:
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=media.caption.html if media.caption else None,
        )
    except ValidationError:
        logger.exception('Error occurred while saving file in database')
        return False, 2
    else:
        try:
            await file.commit()
        except DuplicateKeyError:      
            logger.warning(
                f'{getattr(media, "file_name", "NO_FILE")} is already saved in database'
            )

            return False, 0
        else:
            logger.info(f'{getattr(media, "file_name", "NO_FILE")} is saved to database')
            return True, 1


def clean_query(query):
    """Remove common noise words from search query"""
    words = query.split()
    cleaned = [w for w in words if w.lower() not in FILTER_WORDS]
    return ' '.join(cleaned).strip() if cleaned else query


# ------ Pagination Result Cache ------
# Caches search results so page 2+ don't re-scan 700K+ docs with regex.
# First search: normal DB query + cache the results.
# Page 2+: served instantly from memory (zero DB queries).
_search_cache = {}
_CACHE_TTL = 300          # 5 minutes
_MAX_CACHE_RESULTS = 200  # Cache up to 200 results per query (~20 pages)
_MAX_CACHE_ENTRIES = 50   # Max simultaneous cached queries (keeps RAM < 10MB)


def _cleanup_search_cache():
    """Remove expired entries from search cache"""
    now = _time.time()
    expired = [k for k, v in _search_cache.items() if now - v['time'] >= _CACHE_TTL]
    for k in expired:
        del _search_cache[k]


def clear_search_cache():
    """Public: clear entire search cache (call after bulk file add/delete if needed)"""
    _search_cache.clear()


async def _perform_search(query, file_type, max_results, offset, cached_total=None):
    """Build regex from query and search MongoDB"""
    # Normalize: strip parentheses/brackets so (2012) is treated same as 2012
    query = re.sub(r'[(){}\[\]]', ' ', query)
    query = re.sub(r'\s+', ' ', query).strip()
    
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.+\-_()\[\]])' + query + r'(\b|[\.+\-_()\[\]])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.+\-_()\[\]]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return [], '', 0

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    # --- Check search cache (pages 2+ served instantly from memory) ---
    cache_key = f"{raw_pattern}:{file_type}"
    now = _time.time()
    cached = _search_cache.get(cache_key)

    if cached and (now - cached['time']) < _CACHE_TTL:
        # ✅ CACHE HIT — zero DB queries!
        all_files = cached['files']
        total_results = cached['total']

        if offset < len(all_files):
            files = all_files[offset:offset + max_results]
        elif total_results > len(all_files):
            # Beyond cached range — fallback to DB for very deep pages
            cursor = Media.find(filter)
            cursor.sort('$natural', -1)
            cursor.skip(offset).limit(max_results)
            files = await cursor.to_list(length=max_results)
        else:
            files = []

        next_offset = offset + max_results
        if next_offset > total_results:
            next_offset = ''
        return files, next_offset, total_results

    # --- CACHE MISS — query DB and cache results for future pages ---
    cursor = Media.find(filter)
    cursor.sort('$natural', -1)  # Preserve original insertion-order sort

    if cached_total is not None:
        # Total already known from BUTTONS dict — skip count_documents
        all_files = await cursor.to_list(length=_MAX_CACHE_RESULTS)
        total_results = cached_total
    else:
        # Run both in parallel (preserves original asyncio.gather pattern)
        all_files, count = await asyncio.gather(
            cursor.to_list(length=_MAX_CACHE_RESULTS),
            Media.count_documents(filter)
        )
        # Smart total: use actual length when all results fit in cache
        total_results = len(all_files) if len(all_files) < _MAX_CACHE_RESULTS else count

    # Store in cache (with cleanup if full)
    if len(_search_cache) >= _MAX_CACHE_ENTRIES:
        _cleanup_search_cache()
        if len(_search_cache) >= _MAX_CACHE_ENTRIES:
            oldest = sorted(_search_cache, key=lambda k: _search_cache[k]['time'])[:10]
            for k in oldest:
                del _search_cache[k]

    _search_cache[cache_key] = {
        'files': all_files,
        'total': total_results,
        'time': now
    }

    # Return requested page from freshly cached results
    files = all_files[offset:offset + max_results]

    next_offset = offset + max_results
    if next_offset > total_results:
        next_offset = ''

    return files, next_offset, total_results


async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0, filter=False, cached_total=None):
    """For given query return (results, next_offset)"""
    if chat_id is not None:
        settings = await get_settings(int(chat_id))
        try:
            if settings['max_btn']:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)
        except KeyError:
            await save_group_settings(int(chat_id), 'max_btn', False)
            settings = await get_settings(int(chat_id))
            if settings['max_btn']:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)
    query = query.strip()
    
    # First pass: search with original query (unchanged behavior)
    files, next_offset, total_results = await _perform_search(query, file_type, max_results, offset, cached_total=cached_total)
    
    # Second pass: if no results and query has multiple words, try removing noise words
    if total_results == 0 and ' ' in query:
        cleaned = clean_query(query)
        if cleaned and cleaned != query:
            files, next_offset, total_results = await _perform_search(cleaned, file_type, max_results, offset)
    
    return files, next_offset, total_results

async def get_bad_files(query, file_type=None, max_results=1000, offset=0, filter=False):
    """For given query return (results, next_offset)"""
    query = query.strip()
    #if filter:
        #better ?
        #query = query.replace(' ', r'(\s|\.|\+|\-|_)')
        #raw_pattern = r'(\s|_|\-|\.|\+)' + query + r'(\s|_|\-|\.|\+)'
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.+\-_])' + query + r'(\b|[\.+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return [], '', 0

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    # Run count and find in parallel instead of sequentially
    cursor = Media.find(filter)
    cursor.sort('$natural', -1)
    cursor.skip(offset).limit(max_results)
    
    files, total_results = await asyncio.gather(
        cursor.to_list(length=max_results),
        Media.count_documents(filter)
    )

    next_offset = offset + max_results
    if next_offset > total_results:
        next_offset = ''

    return files, next_offset, total_results

async def get_file_details(query):
    filter = {'file_id': query}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    return filedetails


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
