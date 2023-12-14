BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "customers" (
	"id"	INTEGER,
	"name"	TEXT,
	"email"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "products" (
	"id"	INTEGER,
	"product"	TEXT,
	"price"	INTEGER,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "orders" (
	"id"	INTEGER,
	"customer_id"	TEXT,
	"created_at"	DATE,
	"updated_at"	DATE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "order_details" (
	"id"	INTEGER,
	"order_id"	INTEGER,
	"product_id"	INTEGER,
	"quantity"	INTEGER,
	"created_at"	DATE,
	PRIMARY KEY("id")
);
INSERT INTO "customers" VALUES (1,'Duvall','duvall@gmail.com');
INSERT INTO "customers" VALUES (2,'Arvin','arvin@gmail.com');
INSERT INTO "customers" VALUES (3,'Mark','mark@gmail.com');
INSERT INTO "customers" VALUES (4,'Ferdinand','isko@gmail.com');
INSERT INTO "customers" VALUES (5,'Rico','rico@gmail.com');
INSERT INTO "products" VALUES (1,'Walis',500);
INSERT INTO "products" VALUES (2,'Bunot',300);
INSERT INTO "products" VALUES (3,'Basahan',200);
INSERT INTO "orders" VALUES (1,'1','2023-11-20','2023-12-14');
INSERT INTO "orders" VALUES (2,'1','2023-12-14',NULL);
INSERT INTO "order_details" VALUES (1,1,1,2,NULL);
INSERT INTO "order_details" VALUES (2,2,2,5,NULL);
INSERT INTO "order_details" VALUES (3,1,2,1,NULL);
CREATE INDEX IF NOT EXISTS "idx_order_date" ON "orders" (
	"created_at"
);
CREATE TRIGGER update_date 
                    AFTER INSERT ON order_details
                    FOR EACH ROW
                    BEGIN
                        UPDATE orders SET updated_at = DATE('now') WHERE id = NEW.order_id;
                    END;
COMMIT;
