ALTER TABLE sar_scenes ALTER COLUMN status DROP DEFAULT;
ALTER TABLE sar_scenes ALTER COLUMN status TYPE scene_status USING status::scene_status;
ALTER TABLE sar_scenes ALTER COLUMN status SET DEFAULT 'queued'::scene_status;

ALTER TABLE users ALTER COLUMN status DROP DEFAULT;
ALTER TABLE users ALTER COLUMN status TYPE user_status USING status::user_status;
ALTER TABLE users ALTER COLUMN status SET DEFAULT 'pending'::user_status;

ALTER TABLE notifications ALTER COLUMN status DROP DEFAULT;
ALTER TABLE notifications ALTER COLUMN status TYPE notif_status USING status::notif_status;
ALTER TABLE notifications ALTER COLUMN status SET DEFAULT 'pending'::notif_status;

ALTER TABLE notification_deliveries ALTER COLUMN status DROP DEFAULT;
ALTER TABLE notification_deliveries ALTER COLUMN status TYPE delivery_status USING status::delivery_status;
ALTER TABLE notification_deliveries ALTER COLUMN status SET DEFAULT 'pending'::delivery_status;

ALTER TABLE bulletins ALTER COLUMN status DROP DEFAULT;
ALTER TABLE bulletins ALTER COLUMN status TYPE bulletin_status USING status::bulletin_status;
ALTER TABLE bulletins ALTER COLUMN status SET DEFAULT 'draft'::bulletin_status;

ALTER TABLE dispatch_tasks ALTER COLUMN column_state DROP DEFAULT;
ALTER TABLE dispatch_tasks ALTER COLUMN column_state TYPE dispatch_state USING column_state::dispatch_state;
ALTER TABLE dispatch_tasks ALTER COLUMN column_state SET DEFAULT 'queued'::dispatch_state;

