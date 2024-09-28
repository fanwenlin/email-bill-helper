from datetime import datetime, timedelta
from src.table import search_raw_items, update_bill_items, BillItem
import lark_oapi.api.bitable.v1 as bitable

BATCH_SIZE = 50

def update_unique_id(record: bitable.AppTableRecord) -> bitable.AppTableRecord:
    fields = record.fields
    bill_value_cent = int(float(fields.get('RMB金额', 0)) * 100)
    bill_time = datetime.fromtimestamp(int(fields.get('时间', 0)) / 1000)
    bill_detail = fields.get('标题', '')
    source_id = fields.get('unique_id', '0').split('_')[0]

    bill_item = BillItem(bill_value_cent, bill_time, bill_detail, source_id)
    new_unique_id = bill_item.unique_id

    if new_unique_id != fields.get('unique_id'):
        # fields['unique_id'] = new_unique_id
        new_fields = {
            'unique_id': new_unique_id
        }
        record.fields = new_fields
        return record
    return None

def batch_update_unique_ids():
    page_token = None
    has_more = True
    total_updated = 0

    while has_more:
        records, page_token, has_more = search_raw_items(page_size=BATCH_SIZE, page_token=page_token, end_time=datetime.now() - timedelta(days=365), start_time=datetime.now() - timedelta(days=765))
        
        if not records:
            print("No more records found")
            break
        
        updated_records = [update_unique_id(record) for record in records]
        updated_records = [record for record in updated_records if record is not None]
        
        if updated_records:
            response = update_bill_items(updated_records)
            total_updated += len(updated_records)
            print(f"Updated {len(updated_records)} records. Total updated: {total_updated}. Response: {response}")
        else:
            print("No records needed updating in this batch")

        print(f"Processed batch. Next page token: {page_token}")

    print(f"Finished updating unique_ids. Total records updated: {total_updated}")

if __name__ == "__main__":
    batch_update_unique_ids()
