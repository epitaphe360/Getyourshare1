-- =============================================================================
-- Migration: Email Verification Support
-- Description: Adds columns required to manage email verification workflow.
-- Date: 2025-10-26
-- =============================================================================

-- 1. Columns for email verification state
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS verification_token TEXT,
    ADD COLUMN IF NOT EXISTS verification_expires TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS verification_sent_at TIMESTAMP WITH TIME ZONE;

-- 2. Ensure future rows default to not verified
ALTER TABLE users ALTER COLUMN email_verified SET DEFAULT FALSE;

-- 3. Backfill legacy rows so existing accounts remain usable
UPDATE users
SET email_verified = COALESCE(email_verified, TRUE)
WHERE email_verified IS NULL;

-- 4. Index token lookups for verification endpoints
CREATE INDEX IF NOT EXISTS idx_users_verification_token
    ON users(verification_token)
    WHERE verification_token IS NOT NULL;
