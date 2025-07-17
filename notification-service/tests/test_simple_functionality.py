"""
Simple working tests to verify our test setup
"""
import pytest
from datetime import datetime, timezone


class TestBasicFunctionality:
    """Test basic functionality to verify test setup."""
    
    def test_datetime_functionality(self):
        """Test basic datetime functionality."""
        now = datetime.now(timezone.utc)
        assert now is not None
        assert isinstance(now, datetime)
    
    def test_string_operations(self):
        """Test basic string operations."""
        test_path = "/projects/test/tasks"
        parts = test_path.strip('/').split('/')
        
        assert len(parts) == 3
        assert parts[0] == "projects"
        assert parts[2] == "tasks"
    
    def test_list_operations(self):
        """Test basic list operations."""
        notification_types = ["created", "updated", "deleted"]
        
        assert len(notification_types) == 3
        assert "created" in notification_types
        assert "invalid" not in notification_types
    
    def test_dict_operations(self):
        """Test basic dictionary operations."""
        payload = {
            "event_type": "task.completed",
            "data": {"user": "john"},
            "metadata": {"source": "api"}
        }
        
        assert payload["event_type"] == "task.completed"
        assert payload.get("data", {}).get("user") == "john"
        assert payload.get("invalid") is None


class TestPathMatching:
    """Test path matching logic (independent implementation)."""
    
    def _path_matches_subscription(self, event_path: str, subscription_path: str, include_children: bool) -> bool:
        """Test implementation of path matching logic."""
        # Normalize paths
        event_path = event_path.rstrip('/')
        subscription_path = subscription_path.rstrip('/')
        
        # Exact match
        if event_path == subscription_path:
            return True
        
        # Child match (if enabled)
        if include_children and event_path.startswith(subscription_path + '/'):
            return True
        
        return False
    
    def test_exact_path_match(self):
        """Test exact path matching."""
        result = self._path_matches_subscription(
            "/projects/test", 
            "/projects/test", 
            False
        )
        assert result is True
    
    def test_child_path_match_enabled(self):
        """Test child path matching when enabled."""
        result = self._path_matches_subscription(
            "/projects/test/tasks/1", 
            "/projects/test", 
            True
        )
        assert result is True
    
    def test_child_path_match_disabled(self):
        """Test child path matching when disabled."""
        result = self._path_matches_subscription(
            "/projects/test/tasks/1", 
            "/projects/test", 
            False
        )
        assert result is False
    
    def test_no_match(self):
        """Test when paths don't match."""
        result = self._path_matches_subscription(
            "/projects/other", 
            "/projects/test", 
            True
        )
        assert result is False
    
    def test_root_path_matching(self):
        """Test root path matching."""
        result = self._path_matches_subscription(
            "/projects/test", 
            "/", 
            True
        )
        assert result is True
    
    def test_trailing_slash_handling(self):
        """Test handling of trailing slashes."""
        result = self._path_matches_subscription(
            "/projects/test/", 
            "/projects/test", 
            False
        )
        assert result is True


class TestNotificationFiltering:
    """Test notification filtering logic."""
    
    def _should_notify(self, notification_types, event_type: str) -> bool:
        """Test implementation of notification filtering."""
        # If no filter, allow all
        if not notification_types:
            return True
        
        # Check if event type is in allowed types
        return event_type in notification_types
    
    def test_filter_match(self):
        """Test filtering with matching type."""
        result = self._should_notify(
            ["task.completed", "task.failed"], 
            "task.completed"
        )
        assert result is True
    
    def test_filter_no_match(self):
        """Test filtering with non-matching type."""
        result = self._should_notify(
            ["task.failed", "task.started"], 
            "task.completed"
        )
        assert result is False
    
    def test_no_filter(self):
        """Test no filtering (allow all)."""
        result = self._should_notify([], "task.completed")
        assert result is True
        
        result = self._should_notify(None, "task.completed")
        assert result is True


class TestTitleGeneration:
    """Test notification title generation logic."""
    
    def _generate_title(self, path: str, event_type: str) -> str:
        """Test implementation of title generation."""
        # Extract object name from path
        parts = path.strip('/').split('/')
        object_name = parts[-1] if parts and parts[0] else "item"
        
        # Capitalize and format for display
        object_display = object_name.replace('-', ' ').replace('_', ' ').title()
        
        if event_type == "created":
            return f"New {object_display} created"
        elif event_type == "updated":
            return f"{object_display} was updated"
        elif event_type == "deleted":
            return f"{object_display} was deleted"
        elif event_type == "commented":
            return f"New comment on {object_display}"
        else:
            return f"{event_type.replace('_', ' ').title()} on {object_display}"
    
    def test_created_title(self):
        """Test title generation for created events."""
        title = self._generate_title("/projects/test-project/tasks/task-1", "created")
        assert "New Task" in title and "created" in title
    
    def test_updated_title(self):
        """Test title generation for updated events."""
        title = self._generate_title("/projects/test-project/tasks/task-1", "updated")
        assert "Task" in title and "was updated" in title
    
    def test_deleted_title(self):
        """Test title generation for deleted events."""
        title = self._generate_title("/projects/test-project/tasks/task-1", "deleted")
        assert "Task" in title and "was deleted" in title
    
    def test_commented_title(self):
        """Test title generation for comment events."""
        title = self._generate_title("/projects/test-project/tasks/task-1", "commented")
        assert "New comment on Task" in title
    
    def test_custom_event_title(self):
        """Test title generation for custom events."""
        title = self._generate_title("/projects/test-project/tasks/task-1", "task_completed")
        assert "Task Completed on Task" in title
    
    def test_title_with_underscores(self):
        """Test title generation with underscore in object name."""
        title = self._generate_title("/projects/test_project/items/my_item", "created")
        assert "New My Item created" in title
    
    def test_title_with_dashes(self):
        """Test title generation with dashes in object name."""
        title = self._generate_title("/projects/test-project/items/my-item", "created")
        assert "New My Item created" in title


class TestContentGeneration:
    """Test notification content generation logic."""
    
    def _generate_content(self, path: str, event_type: str, payload: dict) -> str:
        """Test implementation of content generation."""
        # Extract object name from path
        parts = path.strip('/').split('/')
        object_name = parts[-1] if parts and parts[0] else "item"
        object_display = object_name.replace('-', ' ').replace('_', ' ').title()
        
        # Get data from payload
        data = payload.get("data", {})
        user_name = data.get("user_name", "Someone")
        
        if event_type == "created":
            return f"{user_name} created a new {object_display}"
        elif event_type == "updated":
            return f"{user_name} updated {object_display}"
        elif event_type == "deleted":
            return f"{user_name} deleted {object_display}"
        elif event_type == "commented":
            comment = data.get("comment", "")
            if comment:
                return f"{user_name} commented on {object_display}: {comment[:50]}..."
            return f"{user_name} commented on {object_display}"
        else:
            return f"{user_name} performed {event_type} on {object_display}"
    
    def test_created_content(self):
        """Test content generation for created events."""
        payload = {"data": {"user_name": "John Doe"}}
        content = self._generate_content("/projects/test/tasks/task-1", "created", payload)
        assert "John Doe created a new Task" in content
    
    def test_updated_content(self):
        """Test content generation for updated events."""
        payload = {"data": {"user_name": "Jane Smith"}}
        content = self._generate_content("/projects/test/tasks/task-1", "updated", payload)
        assert "Jane Smith updated Task" in content
    
    def test_commented_content_with_comment(self):
        """Test content generation for comment events with comment text."""
        payload = {"data": {"user_name": "Bob", "comment": "This looks great!"}}
        content = self._generate_content("/projects/test/tasks/task-1", "commented", payload)
        assert "Bob commented on Task" in content and "This looks great!" in content
    
    def test_commented_content_without_comment(self):
        """Test content generation for comment events without comment text."""
        payload = {"data": {"user_name": "Alice"}}
        content = self._generate_content("/projects/test/tasks/task-1", "commented", payload)
        assert "Alice commented on Task" in content
    
    def test_content_with_default_user(self):
        """Test content generation with default user name."""
        payload = {}
        content = self._generate_content("/projects/test/tasks/task-1", "created", payload)
        assert "Someone created a new Task" in content
    
    def test_custom_event_content(self):
        """Test content generation for custom events."""
        payload = {"data": {"user_name": "Charlie"}}
        content = self._generate_content("/projects/test/tasks/task-1", "task_completed", payload)
        assert "Charlie performed task_completed on Task" in content
