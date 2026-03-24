-- VENUE SERVICE - db_venue
-- Таблицы: companies, venues, payouts, venue_documents

CREATE SCHEMA IF NOT EXISTS "venue";

CREATE TABLE "venue"."companies" (
    "id" BIGSERIAL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "inn" VARCHAR(20),
    "is_active" BOOLEAN DEFAULT TRUE,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMP WITH TIME ZONE
);


CREATE TABLE "venue"."venues" (
    "id" BIGSERIAL PRIMARY KEY,
    "company_id" BIGINT,
    "name" VARCHAR(255) NOT NULL,
    "address" TEXT NOT NULL,
    "latitude" DECIMAL(9, 6),
    "longitude" DECIMAL(9, 6),
    "phone" VARCHAR(20),
    "commission_rate" DECIMAL(5, 2) DEFAULT 10.00,
    "payout_balance" DECIMAL(10, 2) DEFAULT 0.00,
    "work_schedule" JSONB DEFAULT '{}',
    "is_open" BOOLEAN DEFAULT TRUE,
    "rating" DECIMAL(3, 2) DEFAULT 0.00,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMP WITH TIME ZONE,
    CONSTRAINT "fk_venues_company" FOREIGN KEY ("company_id") REFERENCES "venue"."companies"("id") ON DELETE SET NULL
);
CREATE INDEX "venues_idx_company" ON "venue"."venues" ("company_id");
CREATE INDEX "venues_idx_location" ON "venue"."venues" ("latitude", "longitude");
CREATE INDEX "venues_idx_open" ON "venue"."venues" ("is_open", "deleted_at");


CREATE TABLE "venue"."payouts" (
    "id" BIGSERIAL PRIMARY KEY,
    "venue_id" BIGINT NOT NULL,
    "amount" DECIMAL(10, 2) NOT NULL,
    "period_start" DATE NOT NULL,
    "period_end" DATE NOT NULL,
    "status" VARCHAR(50) DEFAULT 'pending',
    "payment_details" JSONB DEFAULT '{}',
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "paid_at" TIMESTAMP WITH TIME ZONE,
    CONSTRAINT "fk_payouts_venue" FOREIGN KEY ("venue_id") REFERENCES "venue"."venues"("id") ON DELETE RESTRICT
);
CREATE INDEX "payouts_idx_venue" ON "venue"."payouts" ("venue_id", "status");


CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_venues_updated_at BEFORE UPDATE ON "venue"."venues" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
