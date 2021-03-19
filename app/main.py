# importfunctionต่างของ api
import uvicorn
from fastapi import FastAPI, Path, Query, HTTPException
from starlette.responses import JSONResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

# เชื่อมกับ Mongo
from database.mongodb import MongoDB
from config.development import config
from model.rides import (
    createRidesModel,
    updateRidesModel,
)  # importfunction c&u เข้าตาราง

mongo_config = config["mongo_config"]
print("Mongo_config", mongo_config)

# "host" :"location",
# "port" : "27017",
# "user" : "rooi",
# "password" : "rooi",
# "auth" : "admin",
# "db" : "waterpark",
# "collection" : "rides",

mongo_db = MongoDB(
    mongo_config["host"],
    mongo_config["port"],
    mongo_config["user"],
    mongo_config["password"],
    mongo_config["auth_db"],
    mongo_config["db"],
    mongo_config["collection"],
)
mongo_db._connect()  # กับdb

# use API
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# อ่านข้อมูล db return 200 คือปกติ
@app.get("/")
def index():
    return JSONResponse(content={"message": "Rides Info"}, status_code=200)


#!อ่านข้อมูลในdb มีการsortโดยเรียงmenu_typeตามตัวอักษร A-Z , Z-A
@app.get("/rides/")
def get_rides(
    sort_by: Optional[str] = None,
    order: Optional[str] = Query(None, min_length=3, max_length=4),
):

    try:
        result = mongo_db.find(sort_by, order)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")
        # หากเป็น 500 ให้แสดงใน Terminal

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


# pathเพื่อส่งพาร rides_id เพื่อหาข้อมูล
@app.get("/rides/{rides_id}")
def get_rides_by_id(
    rides_id: str = Path(None, min_length=10, max_length=10)
):  # ID ที่ใส่มาไม่ควรเกิน 10
    try:
        result = mongo_db.find_one(rides_id)  # rides ควรมีอันเดียว
    except:
        raise HTTPException(
            status_code=500, detail="Something went wrong !!"
        )  # api error

    if result is None:
        raise HTTPException(status_code=404, detail="Rides Id not found !!")  #

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


# สร้างข้อมูลลง db
@app.post("/rides")
def create(rides: createRidesModel):
    try:
        rides_id = mongo_db.create(rides)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "rides_id": rides_id,
            },
        },
        status_code=201,
    )


@app.patch("/rides/{rides_id}")
def update_rides(
    rides: updateRidesModel,
    rides_id: str = Path(None, min_length=10, max_length=10),
):
    print("rides", rides)
    try:
        updated_rides_id, modified_count = mongo_db.update(rides_id, rides)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Rides Id: {updated_rides_id} is not update want fields",
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "rides_id": updated_rides_id,
                "modified_count": modified_count,
            },
        },
        status_code=200,
    )


# ลบข้อมูลระบุ ID
@app.delete("/rides/{rides_id}")
def delete_rides_by_id(rides_id: str = Path(None, min_length=10, max_length=10)):
    try:
        deleted_rides_id, rides_count = mongo_db.delete(rides_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if rides_count == 0:
        raise HTTPException(
            status_code=404, detail=f"rides Id: {deleted_rides_id} is Deleted"
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "rides_id": deleted_rides_id,
                "deleted_count": rides_count,
            },
        },
        status_code=200,  # หากลบได้ status code 200 จะแสดงใน terminal คือ ปกติ
    )


if __name__ == "__main__":  # เชื่อม db ใช้ host="127.0.0.1" port = 3001
    uvicorn.run("main:app", host="127.0.0.1", port=3001, reload=True)