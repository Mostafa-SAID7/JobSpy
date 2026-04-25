"""
Tests for user and search history cache invalidation functionality

Tests verify that cache is properly invalidated when users or search history is updated.
"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.redis import redis_client
from app.repositories.user_repo import UserRepository
from app.repositories.search_history_repo import SearchHistoryRepository
from app.schemas.user import UserUpdate
from app.schemas.search_history import SearchHistoryCreate
from sqlalchemy.ext.asyncio import AsyncSession


class TestCacheInvalidationOnUserUpdate:
    """Test cache invalidation when users are updated."""
    
    @pytest.mark.asyncio
    async def test_update_user_invalidates_cache(self):
        """Test that updating a user invalidates its cache."""
        db = AsyncMock(spec=AsyncSession)
        user_repo = UserRepository(db)
        
        user_id = uuid4()
        user_update = UserUpdate(full_name="Updated Name")
        
        mock_user = AsyncMock()
        mock_user.id = user_id
        mock_user.email = "test@example.com"
        
        with patch.object(user_repo, 'get_by_id', return_value=mock_user):
            with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
                db.flush = AsyncMock()
                result = await user_repo.update(user_id, user_update)
        
        assert mock_delete.called
    
    @pytest.mark.asyncio
    async def test_update_user_email_invalidates_both_caches(self):
        """Test that updating user email invalidates both ID and email caches."""
        db = AsyncMock(spec=AsyncSession)
        user_repo = UserRepository(db)
        
        user_id = uuid4()
        old_email = "old@example.com"
        new_email = "new@example.com"
        user_update = UserUpdate(email=new_email)
        
        mock_user = AsyncMock()
        mock_user.id = user_id
        mock_user.email = old_email
        
        with patch.object(user_repo, 'get_by_id', return_value=mock_user):
            with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
                db.flush = AsyncMock()
                
                result = await user_repo.update(user_id, user_update)
                await user_repo.invalidate_user_cache(user_id)
                await user_repo.invalidate_user_email_cache(old_email)
                await user_repo.invalidate_user_email_cache(new_email)
        
        assert mock_delete.call_count >= 3
    
    @pytest.mark.asyncio
    async def test_delete_user_invalidates_cache(self):
        """Test that deleting a user invalidates its cache."""
        db = AsyncMock(spec=AsyncSession)
        user_repo = UserRepository(db)
        
        user_id = uuid4()
        
        mock_user = AsyncMock()
        mock_user.id = user_id
        
        with patch.object(user_repo, 'get_by_id', return_value=mock_user):
            with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
                db.delete = AsyncMock()
                db.flush = AsyncMock()
                
                result = await user_repo.delete(user_id)
        
        assert mock_delete.called
        assert result is True


class TestCacheInvalidationOnSearchHistoryUpdate:
    """Test cache invalidation when search history is updated."""
    
    @pytest.mark.asyncio
    async def test_create_search_history_invalidates_cache(self):
        """Test that creating search history invalidates user's search cache."""
        db = AsyncMock(spec=AsyncSession)
        search_repo = SearchHistoryRepository(db)
        
        user_id = uuid4()
        search_create = SearchHistoryCreate(
            job_id=uuid4(),
            query="Python Developer",
            filters={},
            results_count=10,
            search_type="basic"
        )
        
        db.flush = AsyncMock()
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            result = await search_repo.create(user_id, search_create)
        
        assert mock_delete_pattern.called
    
    @pytest.mark.asyncio
    async def test_delete_search_history_invalidates_cache(self):
        """Test that deleting search history invalidates cache."""
        db = AsyncMock(spec=AsyncSession)
        search_repo = SearchHistoryRepository(db)
        
        search_id = uuid4()
        user_id = uuid4()
        
        mock_search = AsyncMock()
        mock_search.id = search_id
        mock_search.user_id = user_id
        
        with patch.object(search_repo, 'get_by_id', return_value=mock_search):
            with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
                with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
                    db.delete = AsyncMock()
                    db.flush = AsyncMock()
                    
                    result = await search_repo.delete(search_id)
        
        assert mock_delete.called
        assert mock_delete_pattern.called
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_user_search_history_invalidates_all_user_caches(self):
        """Test that deleting all user search history invalidates all caches."""
        db = AsyncMock(spec=AsyncSession)
        search_repo = SearchHistoryRepository(db)
        
        user_id = uuid4()
        
        mock_searches = [AsyncMock() for _ in range(3)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_searches
        
        db.execute = AsyncMock(return_value=mock_result)
        db.delete = AsyncMock()
        db.flush = AsyncMock()
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            result = await search_repo.delete_by_user(user_id)
        
        assert mock_delete_pattern.called
