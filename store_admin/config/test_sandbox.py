# from pydantic import BaseSettings, StrictStr, Field, validator, StrictFloat
# from dotenv import load_dotenv
#
# load_dotenv()
#
#
# class PGConfig(BaseSettings):
#     db: StrictStr = Field(..., env='DB_NAME')
#     user: StrictStr = Field(..., env='DB_USER')
#     password: StrictStr = Field(..., env='DB_PASSWORD')
#
#     @validator('db')
#     def rename_db(cls, raw_name):
#         return 'db_2'
#
#
# test_pg = PGConfig()
# print(test_pg.dict())
# print(test_pg.db)
