CREATE TABLE IF NOT EXISTS "linea" (
	"id_linea" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"nombre" VARCHAR(20) NOT NULL,
	PRIMARY KEY("id_linea")
);

CREATE TABLE IF NOT EXISTS "forma_pago" (
	"id_forma_pago" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"nombre" VARCHAR(30) NOT NULL UNIQUE,
	PRIMARY KEY("id_forma_pago")
);

CREATE TABLE IF NOT EXISTS "cliente" (
	"id_cliente" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"nombre" VARCHAR(30) NOT NULL,
	"paterno" VARCHAR(30) NOT NULL,
	"materno" VARCHAR(30),
	"telefono" VARCHAR(13) UNIQUE,
	"correo" VARCHAR(40) NOT NULL UNIQUE,
	"contrasena" VARCHAR(255) NOT NULL,
	PRIMARY KEY("id_cliente")
);

CREATE TABLE IF NOT EXISTS "titular" (
	"id_titular" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"nombre" VARCHAR(30) NOT NULL,
	"paterno" VARCHAR(30) NOT NULL,
	"materno" VARCHAR(30),
	PRIMARY KEY("id_titular")
);

CREATE TABLE IF NOT EXISTS "pasajero" (
	"id_pasajero" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"nombre" VARCHAR(30) NOT NULL,
	"paterno" VARCHAR(30) NOT NULL,
	"materno" VARCHAR(30),
	PRIMARY KEY("id_pasajero")
);

CREATE TABLE IF NOT EXISTS "pais" (
	"id_pais" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"iso_alfa3" CHAR(3) NOT NULL UNIQUE,
	"nombre" VARCHAR(30) NOT NULL UNIQUE,
	PRIMARY KEY("id_pais"),
	CONSTRAINT "ck_formato_iso_alfa3" CHECK ("iso_alfa3" ~ '^[A-Z]{3}$')
);

CREATE TABLE IF NOT EXISTS "agencia" (
	"id_agencia" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"nombre" VARCHAR(50) NOT NULL,
	PRIMARY KEY("id_agencia")
);

CREATE TABLE IF NOT EXISTS "banco" (
	"id_banco" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"nombre" VARCHAR(30) NOT NULL,
	PRIMARY KEY("id_banco")
);

CREATE TABLE IF NOT EXISTS "medio_transporte" (
	"id_transporte" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_linea" INTEGER NOT NULL,
	"nombre" VARCHAR(20) NOT NULL,
	PRIMARY KEY("id_transporte")
);

CREATE TABLE IF NOT EXISTS "asiento" (
	"id_asiento" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_transporte" INTEGER NOT NULL,
	"num_asiento" VARCHAR(3) NOT NULL,
	PRIMARY KEY("id_asiento")
);

CREATE TABLE IF NOT EXISTS "empleado" (
	"id_empleado" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_agencia" INTEGER NOT NULL,
	"matricula" VARCHAR(9) NOT NULL UNIQUE,
	"nombre" VARCHAR(30) NOT NULL,
	"paterno" VARCHAR(30) NOT NULL,
	"materno" VARCHAR(30),
	"telefono" VARCHAR(13) UNIQUE,
	"correo" VARCHAR(40) NOT NULL UNIQUE,
	"contrasena" VARCHAR(255) NOT NULL,
	PRIMARY KEY("id_empleado")
);

CREATE TABLE IF NOT EXISTS "estado" (
	"id_estado" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_pais" INTEGER NOT NULL,
	"nombre" VARCHAR(40) NOT NULL,
	PRIMARY KEY("id_estado")
);

CREATE TABLE IF NOT EXISTS "cuenta" (
	"id_cuenta" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_titular" INTEGER NOT NULL,
	"id_banco" INTEGER NOT NULL,
	"num_cuenta" VARCHAR(18) NOT NULL,
	PRIMARY KEY("id_cuenta")
);

CREATE TABLE IF NOT EXISTS "tarjeta" (
	"id_tarjeta" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_cuenta" INTEGER NOT NULL,
	"tipo_tarjeta" VARCHAR(20) NOT NULL,
	"ultimos4" CHAR(4) NOT NULL,
	PRIMARY KEY("id_tarjeta")
);

CREATE TABLE IF NOT EXISTS "ciudad" (
	"id_ciudad" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_estado" INTEGER NOT NULL,
	"nombre" VARCHAR(30) NOT NULL,
	PRIMARY KEY("id_ciudad")
);

CREATE TABLE IF NOT EXISTS "viaje" (
	"id_viaje" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_transporte" INTEGER NOT NULL,
	"id_ciudad_destino" INTEGER NOT NULL,
	"id_ciudad_origen" INTEGER NOT NULL,
	"fecha_salida" TIMESTAMP NOT NULL,
	"fecha_llegada" TIMESTAMP NOT NULL,
	"costo" NUMERIC(8,2) NOT NULL,
	PRIMARY KEY("id_viaje"),
	CONSTRAINT "ck_id_ciudad_destino_id_ciudad_origen" CHECK ("id_ciudad_origen" <> "id_ciudad_destino"),
	CONSTRAINT "ck_fecha_salida_fecha_llegada" CHECK ("fecha_salida" < "fecha_llegada"),
	CONSTRAINT "ck_costo_no_cero" CHECK ("costo" > 0)
);

CREATE TABLE IF NOT EXISTS "agencia_viaje" (
	"id_agencia" INTEGER NOT NULL,
	"id_viaje" INTEGER NOT NULL,
	PRIMARY KEY("id_agencia", "id_viaje")
);

CREATE TABLE IF NOT EXISTS "reserva" (
	"id_reserva" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_viaje" INTEGER NOT NULL,
	"id_agencia" INTEGER NOT NULL,
	"id_cliente" INTEGER NOT NULL,
	"fecha_reserva" TIMESTAMPTZ NOT NULL,
	"id_estado_pago" INTEGER NOT NULL,
	PRIMARY KEY("id_reserva"),
	CONSTRAINT "reserva_unique_0" UNIQUE ("id_reserva", "id_viaje")
);

CREATE TABLE IF NOT EXISTS "detalles_reserva" (
	"id_detalles_reserva" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_reserva" INTEGER NOT NULL,
	"id_viaje" INTEGER NOT NULL,
	"id_pasajero" INTEGER NOT NULL,
	"id_documento_identidad" INTEGER NOT NULL,
	"id_asiento" INTEGER NOT NULL,
	PRIMARY KEY("id_detalles_reserva"),
	CONSTRAINT "reserva_pasajero_unique_1" UNIQUE ("id_viaje", "id_asiento"),
	CONSTRAINT "reserva_pasajero_unique_3" UNIQUE ("id_pasajero", "id_viaje")
);

CREATE TABLE IF NOT EXISTS "parcialidad" (
	"id_parcialidad" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_factura" INTEGER NOT NULL,
	"num_parcia" SMALLINT NOT NULL,
	"fecha_vencimiento" DATE NOT NULL,
	"total_parcia" NUMERIC(8,2) NOT NULL,
	PRIMARY KEY("id_parcialidad"),
	CONSTRAINT "ck_total_parcia_no_cero" CHECK ("total_parcia" > 0)
);

CREATE TABLE IF NOT EXISTS "boleto" (
	"id_boleto" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_detalles_reserva" INTEGER NOT NULL,
	"num_boleto" VARCHAR(16) NOT NULL UNIQUE,
	"fecha_emision" TIMESTAMP NOT NULL,
	"precio" NUMERIC(8,2) NOT NULL,
	PRIMARY KEY("id_boleto"),
	CONSTRAINT "ck_precio_no_cero" CHECK ("precio" > 0)
);

CREATE TABLE IF NOT EXISTS "pago" (
	"id_pago" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_parcialidad" INTEGER,
	"id_forma_pago" INTEGER NOT NULL,
	"id_tarjeta" INTEGER,
	"id_factura" INTEGER,
	"monto_pago" NUMERIC(8,2) NOT NULL,
	"fecha_pago" TIMESTAMPTZ NOT NULL,
	PRIMARY KEY("id_pago"),
	CONSTRAINT "ck_monto_pago_no_cero" CHECK ("monto_pago" > 0),
	CONSTRAINT "ck_contado_o_parcialidad" CHECK ((id_factura IS NOT NULL AND id_parcialidad IS NULL) OR 
       (id_factura IS NULL AND id_parcialidad IS NOT NULL))
);

CREATE TABLE IF NOT EXISTS "factura" (
	"id_factura" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_reserva" INTEGER NOT NULL,
	"id_viaje" INTEGER NOT NULL,
	"fecha_emision" TIMESTAMPTZ NOT NULL,
	"total_factura" NUMERIC(8, 2) NOT NULL,
	"metodo_pago" VARCHAR(3) NOT NULL,
	PRIMARY KEY("id_factura"),
	CONSTRAINT "ck_total_factura_no_cero" CHECK ("total_factura" > 0),
	CONSTRAINT "ck_metodos_de_pago" CHECK("metodo_pago" IN ('PUE', 'PPD'))
);

CREATE TABLE IF NOT EXISTS "estado_pago" (
	"id_estado_pago" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"nombre" VARCHAR(40) NOT NULL UNIQUE,
	PRIMARY KEY("id_estado_pago")
);

CREATE TABLE IF NOT EXISTS "documento_identidad" (
	"id_documento_identidad" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
	"id_pasajero" INTEGER NOT NULL,
	"id_pais_emision" INTEGER NOT NULL,
	"tipo_documento" VARCHAR(30) NOT NULL,
	"numero_documento" VARCHAR(18) NOT NULL,
	PRIMARY KEY("id_documento_identidad"),
	CONSTRAINT "tipo_documento_identidad_unique_0" UNIQUE ("numero_documento", "tipo_documento", "id_pais_emision"),
	CONSTRAINT "documento_identidad_unique_1" UNIQUE ("id_pasajero", "id_documento_identidad")
);

ALTER TABLE "parcialidad"
ADD FOREIGN KEY("id_factura") REFERENCES "factura"("id_factura")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "medio_transporte"
ADD FOREIGN KEY("id_linea") REFERENCES "linea"("id_linea")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "asiento"
ADD FOREIGN KEY("id_transporte") REFERENCES "medio_transporte"("id_transporte")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "empleado"
ADD FOREIGN KEY("id_agencia") REFERENCES "agencia"("id_agencia")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "cuenta"
ADD FOREIGN KEY("id_banco") REFERENCES "banco"("id_banco")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "cuenta"
ADD FOREIGN KEY("id_titular") REFERENCES "titular"("id_titular")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "tarjeta"
ADD FOREIGN KEY("id_cuenta") REFERENCES "cuenta"("id_cuenta")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "ciudad"
ADD FOREIGN KEY("id_estado") REFERENCES "estado"("id_estado")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "viaje"
ADD FOREIGN KEY("id_ciudad_origen") REFERENCES "ciudad"("id_ciudad")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "viaje"
ADD FOREIGN KEY("id_ciudad_destino") REFERENCES "ciudad"("id_ciudad")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "viaje"
ADD FOREIGN KEY("id_transporte") REFERENCES "medio_transporte"("id_transporte")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "agencia_viaje"
ADD FOREIGN KEY("id_agencia") REFERENCES "agencia"("id_agencia")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "agencia_viaje"
ADD FOREIGN KEY("id_viaje") REFERENCES "viaje"("id_viaje")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "reserva"
ADD FOREIGN KEY("id_agencia", "id_viaje") REFERENCES "agencia_viaje"("id_agencia", "id_viaje")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "pago"
ADD FOREIGN KEY("id_tarjeta") REFERENCES "tarjeta"("id_tarjeta")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "pago"
ADD FOREIGN KEY("id_forma_pago") REFERENCES "forma_pago"("id_forma_pago")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "reserva"
ADD FOREIGN KEY("id_estado_pago") REFERENCES "estado_pago"("id_estado_pago")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "documento_identidad"
ADD FOREIGN KEY("id_pasajero") REFERENCES "pasajero"("id_pasajero")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "reserva"
ADD FOREIGN KEY("id_cliente") REFERENCES "cliente"("id_cliente")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "factura"
ADD FOREIGN KEY("id_reserva", "id_viaje") REFERENCES "reserva"("id_reserva", "id_viaje")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "detalles_reserva"
ADD FOREIGN KEY("id_documento_identidad", "id_pasajero") REFERENCES "documento_identidad"("id_documento_identidad", "id_pasajero")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "detalles_reserva"
ADD FOREIGN KEY("id_asiento") REFERENCES "asiento"("id_asiento")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "boleto"
ADD FOREIGN KEY("id_detalles_reserva") REFERENCES "detalles_reserva"("id_detalles_reserva")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "detalles_reserva"
ADD FOREIGN KEY("id_reserva", "id_viaje") REFERENCES "reserva"("id_reserva", "id_viaje")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "pago"
ADD FOREIGN KEY("id_factura") REFERENCES "factura"("id_factura")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "pago"
ADD FOREIGN KEY("id_parcialidad") REFERENCES "parcialidad"("id_parcialidad")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "estado"
ADD FOREIGN KEY("id_pais") REFERENCES "pais"("id_pais")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "documento_identidad"
ADD FOREIGN KEY("id_pais_emision") REFERENCES "pais"("id_pais")
ON UPDATE NO ACTION ON DELETE NO ACTION;