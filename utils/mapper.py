
class Mapper:

    @staticmethod
    def map_fields(model, records):
        """Inserts into DB all lines from records to the specified model"""
        fields = [name for name in model._meta.sorted_field_names if name != 'id']
        rows = [dict(zip(fields, record)) for data in records[0] for record in data]

        return rows
