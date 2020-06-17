from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_measurements(startTime, endTime):
        sql = "SELECT * FROM Measurement where DateTime between %s and %s"
        params = [startTime, endTime]
        return Database.get_rows(sql, params)

    @staticmethod
    def log_measurement(deviceid, value):
        sql = "INSERT INTO Measurement(DeviceID, Value) VALUES(%s,%s)"
        params = [deviceid, value]
        return Database.execute_sql(sql, params)

    @staticmethod
    def get_min_max(id):
        sql = "SELECT minimumvalue, maximumvalue FROM Device WHERE ID = %s"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def get_all_min_max():
        sql = "SELECT id, minimumvalue, maximumvalue FROM Device"
        return Database.get_rows(sql)

    @staticmethod
    def update_min_max(min, max, id):
        sql = "update Device set MinimumValue = %s, MaximumValue= %s where id = %s"
        params = [min, max, id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def check_endtime(code):
        sql = "select * from LoggingAction where ActionCode = %s order by StartTime desc limit 1"
        params = [code]
        return Database.get_one_row(sql, params)

    @staticmethod
    def log_off_time(code):
        sql = "update LoggingAction set StopTime = current_timestamp() where ActionCode = %s order by StartTime desc limit 1"
        params = [code]
        return Database.execute_sql(sql, params)

    @staticmethod
    def log_on_time(measurement_id,code):
        sql = "insert into LoggingAction(MeasurementID, ActionCode) values(%s, %s)"
        params = [measurement_id, code]
        return Database.execute_sql(sql, params)

    @staticmethod
    def get_last_measurement():
        sql = "SELECT * FROM Measurement order by DateTime desc LIMIT 1"
        return Database.get_one_row(sql)

    @staticmethod
    def get_plantname():
        sql = "SELECT Name FROM Plant"
        return Database.get_one_row(sql)

    @staticmethod
    def update_plantname(name):
        sql = "update Plant set Name = %s where ID = 1"
        params = [name]
        return Database.execute_sql(sql, params)