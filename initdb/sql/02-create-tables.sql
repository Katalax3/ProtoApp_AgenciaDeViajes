-- Tablas padres

CREATE TABLE IF NOT EXISTS Empleado (
  idEmpleados NUMERIC(9) NOT NULL,
  nombre VARCHAR(30) NOT NULL,
  paterno VARCHAR(30) NOT NULL,
  materno VARCHAR(30) NOT NULL,
  correo VARCHAR(40) NOT NULL,
  contrasena VARCHAR(16) NOT NULL,
  CONSTRAINT pk_Empleados PRIMARY KEY (idEmpleados),
  CONSTRAINT ck_Empleados_Contra CHECK (LENGTH(contrasena) >= 8)
);

CREATE TABLE IF NOT EXISTS Parcialidades (
  idParcia NUMERIC(9) NOT NULL,
  tipoParcia VARCHAR(20) NOT NULL,
  CONSTRAINT pk_Parcialidades PRIMARY KEY (idParcia)
);

CREATE TABLE IF NOT EXISTS Pais (
  idPais NUMERIC(9) NOT NULL,
  nombre VARCHAR(30) NOT NULL,
  CONSTRAINT pk_Pais PRIMARY KEY (idPais)
);

CREATE TABLE IF NOT EXISTS MedioTransporte (
  idTransporte NUMERIC(9) NOT NULL,
  nombre VARCHAR(20) NOT NULL,
  CONSTRAINT pk_MedioTransporte PRIMARY KEY (idTransporte)
);

CREATE TABLE IF NOT EXISTS Clientes (
  idClientes NUMERIC(9) NOT NULL,
  nombre VARCHAR(30) NOT NULL,
  paterno VARCHAR(30) NOT NULL,
  materno VARCHAR(30) NULL,
  telefono VARCHAR(13) NULL,
  correo VARCHAR(40) NULL,
  contrasena VARCHAR(16) NOT NULL,
  CONSTRAINT pk_Clientes PRIMARY KEY (idClientes),
  CONSTRAINT ck_Cliente_Contra CHECK (LENGTH(contrasena) >= 8)
);

CREATE TABLE IF NOT EXISTS Banco (
  idBanco NUMERIC(9) NOT NULL,
  nombre VARCHAR(30) NOT NULL,
  CONSTRAINT pk_Banco PRIMARY KEY (idBanco)
);

CREATE TABLE IF NOT EXISTS Titular (
  idTitular NUMERIC(9) NOT NULL,
  nombre VARCHAR(30) NOT NULL,
  paterno VARCHAR(30) NOT NULL,
  materno VARCHAR(30) NULL,
  CONSTRAINT pk_Titular PRIMARY KEY (idTitular)
);

CREATE TABLE IF NOT EXISTS Pasajero (
  idPasajero NUMERIC(9) NOT NULL,
  nombre VARCHAR(30) NOT NULL,
  paterno VARCHAR(30) NOT NULL,
  materno VARCHAR(30) NULL,
  CONSTRAINT pk_Pasajero PRIMARY KEY (idPasajero)
);

-- Tablas hijos

CREATE TABLE IF NOT EXISTS Ciudad (
  idCiudad NUMERIC(9) NOT NULL,
  idPais NUMERIC(9) NOT NULL,
  nombre VARCHAR(30) NOT NULL,
  CONSTRAINT pk_Ciudad PRIMARY KEY (idCiudad),
  CONSTRAINT fk_Pais_Ciudad FOREIGN KEY (idPais)
    REFERENCES Pais(idPais)
);

CREATE TABLE IF NOT EXISTS AgenciaViajes (
  idAgencia NUMERIC(9) NOT NULL,
  idEmpleados NUMERIC(9) NOT NULL,
  nombre VARCHAR(30) NOT NULL,
  CONSTRAINT pk_AgenciaViajes PRIMARY KEY (idAgencia),
  CONSTRAINT fk_Empleado_AgenciaViajes FOREIGN KEY (idEmpleados)
    REFERENCES Empleados(idEmpleados)
);

CREATE TABLE IF NOT EXISTS Origen (
  idOrigen NUMERIC(9) NOT NULL,
  idCiudad NUMERIC(9) NOT NULL,
  CONSTRAINT pk_Origen PRIMARY KEY (idOrigen),
  CONSTRAINT fk_Ciudad_Origen FOREIGN KEY (idCiudad)
    REFERENCES Ciudad(idCiudad)
);

CREATE TABLE IF NOT EXISTS Destino (
  idDestino NUMERIC(9) NOT NULL,
  idCiudad NUMERIC(9) NOT NULL,
  CONSTRAINT pk_Destino PRIMARY KEY (idDestino),
  CONSTRAINT fk_Ciudad_Destino FOREIGN KEY (idCiudad)
    REFERENCES Ciudad(idCiudad)
);

CREATE TABLE IF NOT EXISTS Tarjeta (
  idTarjeta NUMERIC(16) NOT NULL,
  idBanco NUMERIC(9) NOT NULL,
  idTitular NUMERIC(9) NOT NULL,
  tipo VARCHAR(20) NOT NULL,
  CONSTRAINT pk_Tarjeta PRIMARY KEY (idTarjeta),
  CONSTRAINT fk_Banco_Tarjeta FOREIGN KEY (idBanco)
    REFERENCES Banco(idBanco),
  CONSTRAINT fk_Titular_Tarjeta FOREIGN KEY (idTitular)
    REFERENCES Titular(idTitular),
  CONSTRAINT ck_Tarjeta_Tipo CHECK (tipo IN ('Credito', 'Debito'))
);

CREATE TABLE IF NOT EXISTS Viaje (
  idViaje NUMERIC(9) NOT NULL,
  idAgencia NUMERIC(9) NOT NULL,
  nombre VARCHAR(50) NOT NULL,
  fechaEntrada DATE NOT NULL,
  fechaSalida DATE NOT NULL,
  CONSTRAINT pk_Viaje PRIMARY KEY (idViaje),
  CONSTRAINT fk_AgenciaViajes_Viaje FOREIGN KEY (idAgencia)
    REFERENCES AgenciaViajes(idAgencia),
  CONSTRAINT ck_Viaje_Fechas CHECK (fechaSalida > fechaEntrada)
);

CREATE TABLE IF NOT EXISTS Pago (
  idPago NUMERIC(9) NOT NULL,
  idViaje NUMERIC(9) NOT NULL,
  total NUMERIC(5, 2) NOT NULL,
  CONSTRAINT pk_Pago PRIMARY KEY (idPago, idViaje),
  CONSTRAINT fk_Viaje_Pago FOREIGN KEY (idViaje)
    REFERENCES Viaje(idViaje),
  CONSTRAINT ck_Pago_Total CHECK (total >= 0)
);

CREATE TABLE IF NOT EXISTS Reserva (
  idReserva NUMERIC(9) NOT NULL,
  idClientes NUMERIC(9) NOT NULL,
  idViaje NUMERIC(9) NOT NULL,
  fechaReserva DATE NOT NULL,
  CONSTRAINT pk_Reserva PRIMARY KEY (idReserva, idClientes, idViaje),
  CONSTRAINT fk_Clientes_Reserva FOREIGN KEY (idClientes)
    REFERENCES Clientes(idClientes),
  CONSTRAINT fk_Viaje_Reserva FOREIGN KEY (idViaje)
    REFERENCES Viaje(idViaje)
);

CREATE TABLE IF NOT EXISTS Trayecto (
  idTrayecto NUMERIC(9) NOT NULL,
  Viaje_idViaje NUMERIC(9) NOT NULL,
  idTransporte NUMERIC(9) NOT NULL,
  idOrigen NUMERIC(9) NOT NULL,
  idDestino NUMERIC(9) NOT NULL,
  fechaLlegada DATE NOT NULL,
  fechaIda DATE NOT NULL,
  CONSTRAINT pk_Trayecto PRIMARY KEY (idTrayecto),
  CONSTRAINT fk_Viaje_Trayecto FOREIGN KEY (Viaje_idViaje)
    REFERENCES Viaje(idViaje),
  CONSTRAINT fk_MedioTransporte_Trayecto FOREIGN KEY (idTransporte)
    REFERENCES MedioTransporte(idTransporte),
  CONSTRAINT fk_Origen_Trayecto FOREIGN KEY (idOrigen)
    REFERENCES Origen(idOrigen),
  CONSTRAINT fk_Destino_Trayecto FOREIGN KEY (idDestino)
    REFERENCES Destino(idDestino),
  CONSTRAINT ck_Trayecto_Fechas CHECK (fechaLlegada >= fechaIda)
);

CREATE TABLE IF NOT EXISTS Boleto (
  idBoleto NUMERIC(9) NOT NULL,
  idPasajero NUMERIC(9) NOT NULL,
  idTrayecto NUMERIC(9) NOT NULL,
  precio NUMERIC(5, 2) NOT NULL,
  CONSTRAINT pk_Boleto PRIMARY KEY (idBoleto),
  CONSTRAINT fk_Pasajero_Boleto FOREIGN KEY (idPasajero)
    REFERENCES Pasajero(idPasajero),
  CONSTRAINT fk_Trayecto_Boleto FOREIGN KEY (idTrayecto)
    REFERENCES Trayecto(idTrayecto),
  CONSTRAINT ck_Boleto_Precio CHECK (precio >= 0)
);

CREATE TABLE IF NOT EXISTS RegistroParcia (
  NumParcia NUMERIC(2) NOT NULL,
  idViaje NUMERIC(9) NOT NULL,
  idPago NUMERIC(9) NOT NULL,
  idParcia NUMERIC(9) NOT NULL,
  idTarjeta NUMERIC(16) NOT NULL,
  fechaParcia DATE NULL,
  importe NUMERIC(5, 2) NULL,
  CONSTRAINT pk_RegistroParcia PRIMARY KEY (NumParcia, idViaje, idPago, idParcia),
  CONSTRAINT fk_Pago_RegistroParcia FOREIGN KEY (idPago, idViaje)
    REFERENCES Pago(idPago, idViaje),
  CONSTRAINT fk_Parcialidades_RegistroParcia FOREIGN KEY (idParcia)
    REFERENCES Parcialidades(idParcia),
  CONSTRAINT fk_Tarjeta_RegistroParcia FOREIGN KEY (idTarjeta)
    REFERENCES Tarjeta(idTarjeta),
  CONSTRAINT ck_RegistroParcia_Importe CHECK (importe >= 0)
);
