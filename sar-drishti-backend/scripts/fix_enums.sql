DO $$ BEGIN
    CREATE TYPE scene_status AS ENUM ('queued','processing','done','failed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('rb_ee','seoc_officer','collector','ndrf','gsrtc','bisag_gis','admin');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE user_status AS ENUM ('pending','approved','suspended');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE notif_status AS ENUM ('pending','sent','failed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE bulletin_status AS ENUM ('draft','signed','published');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE delivery_status AS ENUM ('pending','delivered','read','failed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE dispatch_state AS ENUM ('queued','en_route','on_site','resolved');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE road_class AS ENUM ('NH','SH','MDR','ODR');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

ALTER TABLE sar_scenes ALTER COLUMN status TYPE scene_status USING status::scene_status;
ALTER TABLE users ALTER COLUMN role TYPE user_role USING role::user_role;
ALTER TABLE users ALTER COLUMN status TYPE user_status USING status::user_status;
ALTER TABLE roads ALTER COLUMN road_class TYPE road_class USING road_class::road_class;
ALTER TABLE notifications ALTER COLUMN status TYPE notif_status USING status::notif_status;
ALTER TABLE notification_deliveries ALTER COLUMN status TYPE delivery_status USING status::delivery_status;
ALTER TABLE bulletins ALTER COLUMN status TYPE bulletin_status USING status::bulletin_status;
ALTER TABLE dispatch_tasks ALTER COLUMN column_state TYPE dispatch_state USING column_state::dispatch_state;

