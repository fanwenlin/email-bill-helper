from datetime import datetime, timedelta
import time
from typing import List, Optional

import yaml

import lark_oapi as lark

import lark_oapi.api.bitable.v1 as bitable

with open('conf/conf.yaml', 'r') as file:
    config = yaml.safe_load(file)

client: lark.Client = lark.Client.builder() \
    .app_id(config['lark']['app_id']) \
    .app_secret(config['lark']['app_secret']) \
    .domain(lark.FEISHU_DOMAIN) \
    .timeout(30) \
    .log_level(lark.LogLevel.DEBUG) \
    .build()

dest_table_id = config['lark']['table_id']
token = config['lark']['app_token']


def save_bill_items_raw(items: list[dict[str, any]]):
    b = bitable.BatchCreateAppTableRecordRequestBuilder()
    b.table_id(dest_table_id)
    b.app_token(token)

    record_list: list[bitable.AppTableRecord] = []
    for item in items:
        record_list.append(
            bitable.AppTableRecordBuilder().fields(item).build())

    req_body_builder = bitable.BatchCreateAppTableRecordRequestBodyBuilder()
    req_body_builder.records(record_list)
    b.request_body(req_body_builder.build())
    req = b.build()
    resp = client.bitable.v1.app_table_record.batch_create(req)

    return resp


class BillItem(object):
    def __init__(self, bill_value_cent: int, bill_time: datetime, bill_detail: str, source_id: str = '0'):
        self.bill_value_cent = bill_value_cent
        self.bill_time = bill_time

        self.bill_detail = bill_detail
        self.unique_id = f'{source_id}_{self.__hash__()}'

    def __eq__(self, other):
        if not isinstance(other, BillItem):
            return NotImplemented
        return (self.bill_value_cent == other.bill_value_cent) \
            and (self.bill_time.timestamp() == other.bill_time.timestamp()) \
            and (self.bill_detail == other.bill_detail)

    def __hash__(self):
        return hash((self.bill_value_cent, self.bill_time.timestamp(), self.bill_detail))


def save_bill_items(items):

    records = []
    for item in items:
        record = {
            "RMB金额": float(item.bill_value_cent) / 100,
            "一级分类": "待归类",
            "时间": int(item.bill_time.timestamp() * 1000),
            "来源": "信用卡账单",
            "标题": item.bill_detail,
            "unique_id": item.unique_id,
        }
        records.append(record)

    return save_bill_items_raw(records)


def get_recent_bill_items(): 
    req = bitable.ListAppTableRecordRequestBuilder().\
        table_id(dest_table_id).\
        app_token(token).\
        sort('["时间 DESC"]').\
        automatic_fields(True).\
        page_size(5)

    req = req.build()

    
    resp = client.bitable.v1.app_table_record.list(req)
    
    items = [record.fields for record in resp.data.items]
    return items

def search_raw_items(start_time: datetime = None, end_time: datetime = None, page_size: int = 100, page_token: str = None):
    if end_time is None:
        end_time = datetime.now()
    if start_time is None:
        start_time = end_time - timedelta(days=3)

    req = bitable.ListAppTableRecordRequestBuilder().\
        table_id(dest_table_id).\
        app_token(token).\
        sort('["时间 DESC"]').\
        automatic_fields(True).\
        page_size(page_size).\
        filter(f'AND(CurrentValue.[时间] >= TODATE("{start_time.strftime("%Y-%m-%d")}"), CurrentValue.[时间] <= TODATE("{end_time.strftime("%Y-%m-%d")}"))')

    if page_token:
        req.page_token(page_token)

    req = req.build()

    
    resp = client.bitable.v1.app_table_record.list(req)
    
    return resp.data.items, resp.data.page_token, resp.data.has_more

def update_bill_items(items: Optional[List[bitable.AppTableRecord]]):
    records = []
    for item in items:
        
        record_id = item.record_id
        if not record_id:
            print(f"Skipping update for item without record_id: {item}")
            continue
        records.append(bitable.AppTableRecord.builder().record_id(record_id).fields(item.fields).build())

    request = bitable.BatchUpdateAppTableRecordRequest.builder() \
        .app_token(token) \
        .table_id(dest_table_id) \
        .request_body(bitable.BatchUpdateAppTableRecordRequestBody.builder().records(records).build()) \
        .build()

    try:
        response = client.bitable.v1.app_table_record.batch_update(request)
        if not response.success():
            print(f"Failed to batch update records. Error: {response.msg}")
            return f"Batch update failed: {response.msg}"
        else:
            print(f"Successfully batch updated {len(records)} records")
            return f"Successfully batch updated {len(records)} records"
    except Exception as e:
        print(f"Error during batch update: {str(e)}")
        return f"Error during batch update: {str(e)}"


if __name__ == "__main__":
    # Example usage
    items = [BillItem(10000, datetime.now(), "Example Bill Detail")]
    response = save_bill_items(items)
    print(response)
