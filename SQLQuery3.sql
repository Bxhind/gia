CREATE FUNCTION dbo.ValidateStr (@value NVARCHAR(50), @IsINT BIT = 0)
RETURNS NVARCHAR(50)
AS
BEGIN
	SET @value = LTRIM(RTRIM(@value));
	SET @value = REPLACE(@value, ',', '.');
	SET @value = REPLACE(@value, '%', '');
	SET @value = REPLACE(@value, CHAR(160), '');
	SET @value = IIF(@IsINT = 1, CAST(CAST(@value AS FLOAT) AS NVARCHAR(50)), @value);
	
	RETURN @value;
END;
GO

CREATE PROCEDURE ParseField
	@table NVARCHAR(MAX),
	@field NVARCHAR(MAX),
	@type NVARCHAR(MAX)
AS
BEGIN
	DECLARE @sql NVARCHAR(MAX);
	SET @sql = N'
	UPDATE ' + @table + '
	SET ' + @field + ' = dbo.ValidateStr(' + @field + ', ' + IIF(@type = 'INT', '1', '0') + ');
	ALTER TABLE ' + @table + '
	ALTER COLUMN ' + @field + ' ' + @type + ';
	';
	EXEC sp_executesql @sql;
END;
GO

-----------------------------------------------------------------------

DROP DATABASE IF EXISTS gia;
CREATE DATABASE gia

-- Выполняем импорт через Import Data или Import Flat File ...
-- Таблицы type_import и materials_import уже есть

USE gia;
BEGIN TRAN
	ALTER TABLE type_import 
	ADD ID INT IDENTITY(1,1) PRIMARY KEY; -- если нужно, можете через Design перетащить id вверх

	EXEC dbo.ParseField 'type_import', 'perc', 'DECIMAL(10,2)';

	----------------------------------------------------------------------------------------------------------------------

	ALTER TABLE materials_import
	ADD ID INT IDENTITY(1,1) PRIMARY KEY; -- если нужно, можете через Design перетащить id вверх

	EXEC dbo.ParseField 'materials_import', 'cost', 'DECIMAL(10,2)';
	EXEC dbo.ParseField 'materials_import', 'quantity', 'INT';
	EXEC dbo.ParseField 'materials_import', 'min_quantity', 'INT';
	EXEC dbo.ParseField 'materials_import', 'quantity_per_box', 'FLOAT';

	----------------------------------------------------------------------------------------------------------------------

	ALTER TABLE materials_import
	ADD type_id INT;
	GO

	UPDATE mt
	SET mt.type_id = ti.id
	FROM materials_import mt
	JOIN type_import ti ON mt.type_temp = ti.name;

	ALTER TABLE materials_import
	ADD CONSTRAINT FK_type_materials_import 
	FOREIGN KEY (type_id) REFERENCES type_import(id);

	ALTER TABLE materials_import
	DROP COLUMN type_temp;
	GO

	----------------------------------------------------------------------------------------------------------------------

	SELECT * FROM type_import;
	SELECT * FROM materials_import;
	SELECT * FROM materials_import mt JOIN type_import ti ON mt.type_id = ti.id
ROLLBACK

