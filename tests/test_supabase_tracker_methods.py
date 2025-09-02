from unittest.mock import Mock

from core.infrastructure.database.supabase_tracker import SupabaseTracker


def _mock_tracker():
    tracker = SupabaseTracker.__new__(SupabaseTracker)
    tracker.client = Mock()
    tracker.client.table.return_value.insert.return_value.execute.return_value = None
    return tracker


def test_log_rag_document_calls_supabase():
    tracker = _mock_tracker()
    tracker.log_rag_document("run1", "client", "doc.md", None)
    tracker.client.table.assert_called_with("run_documents")
    tracker.client.table.return_value.insert.assert_called()


def test_save_run_content_calls_supabase():
    tracker = _mock_tracker()
    tracker.save_run_content("run1", "client", "workflow", "title", "body", {"a":1})
    tracker.client.table.assert_called_with("content_generations")
    tracker.client.table.return_value.insert.assert_called()
