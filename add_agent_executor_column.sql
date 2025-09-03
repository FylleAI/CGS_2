-- Add agent_executor column to workflow_runs table
-- This column will store information about which agent executor was used

ALTER TABLE workflow_runs 
ADD COLUMN IF NOT EXISTS agent_executor VARCHAR(200);

-- Add comment to document the column
COMMENT ON COLUMN workflow_runs.agent_executor IS 'Information about the agent executor used for this workflow run';

-- Verify the column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'workflow_runs' 
AND column_name = 'agent_executor';
