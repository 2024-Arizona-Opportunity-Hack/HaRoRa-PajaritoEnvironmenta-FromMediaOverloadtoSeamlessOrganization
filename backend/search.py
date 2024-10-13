import structured_llm_output
from pydantic import BaseModel, Field
from typing import Optional

class SearchArgs(BaseModel):
    season: Optional[str] = Field(None, desc='season from Summer, Winter, Fall, and Spring that is asked in the query. Optional')
    tags: list[str] = Field(desc='give list of tags that should be searched in the DB based on the user query and image provided. Can return empty list too', max_length=3)
    location: Optional[str] = Field(None, desc='location eg. city name or country name that is mentioned in the query')
    date_from: Optional[str] = Field(None, desc='if they query mentions a date range, what would be the start date? Return in dd/mm/yyyy format')
    date_to: Optional[str] = Field(None, desc='if they query mentions a date range, what would be the end date? Return in dd/mm/yyyy format')



if __name__ == '__main__':
  inp = '2023 opportunity hack videos'
  results = structured_llm_output.run(
    model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    messages=[structured_llm_output.Message("user", inp)],
    max_retries=3,
    response_model=SearchArgs,
  )
  print(results)
