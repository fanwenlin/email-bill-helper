from datetime import datetime, timedelta

from table import search_raw_items, update_bill_items
import lark_oapi.api.bitable.v1 as bitable

# Constants
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 3, 31)
BATCH_SIZE = 50

def process_record(item: bitable.AppTableRecord) -> dict:
    # Perform your operations on the record here
    # For example:
    data = item.fields

    # operation
    klass = data.get('一级分类', '待归类')
    if isinstance(klass, list):
        # If klass is a list, pick the first non-'待归类' item, or '待归类' if all are '待归类'
        non_default = [k for k in klass if k != '待归类']
        klass = non_default[0] if non_default else '待归类'
    elif isinstance(klass, str) and ',' in klass:
        # If klass is a comma-separated string, split it and pick the first non-'待归类' item
        klass_list = klass.split(',')
        non_default = [k.strip() for k in klass_list if k.strip() != '待归类']
        klass = non_default[0] if non_default else '待归类'
    
    # Update the '一级分类' field with the selected klass
    
    change = {'一级分类': klass}
    item.fields = change
    return item

def batch_process_records():
    
    page_token = None
    hasmore = True
    while hasmore:
        # Fetch a batch of records
        records, page_token, hasmore = search_raw_items(
            start_time=START_DATE,
            end_time=END_DATE,
            page_size=BATCH_SIZE,
            page_token=page_token
        )
        
        if not records: 
            print(f"No records found between {START_DATE} and {END_DATE}")
            break
        
        # Process each record in the batch
        processed_records = [process_record(record) for record in records]
        
        # Update the processed records in the database
        response = update_bill_items(processed_records)
        print(f"Processed and updated {len(processed_records)} records between {START_DATE} and {END_DATE}, next page {page_token}. Response: {response}")

        

        

if __name__ == "__main__":
    batch_process_records()
