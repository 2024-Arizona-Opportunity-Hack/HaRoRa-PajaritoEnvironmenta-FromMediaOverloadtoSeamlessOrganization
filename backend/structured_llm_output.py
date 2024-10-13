import dataclasses
import openai
import os
import re
import yaml

from pydantic import BaseModel, ValidationError
from typing import Optional


@dataclasses.dataclass
class Message:
  role: str
  content: str

def llm_call(model: str, messages: list[Message], temp: float= 0.8):
  message_list = []
  for message in messages:
    if dataclasses.is_dataclass(message):
      message_list.append(dataclasses.asdict(message))
    else:
      message_list.append(message)
  client = openai.OpenAI(api_key=os.environ["TOGETHER_API_KEY"], base_url="https://api.together.xyz/v1")
  res = client.chat.completions.create(model=model, messages=message_list, temperature=temp, max_tokens=1024)
  return res.choices[0].message.content


def generate_response_prompt(model: type(BaseModel)) -> str:
  TAB = "    "
  ret = "Respond in YAML format, following the below Pydantic model:\n```python\n"
  ret += f"from pydantic import BaseModel, Field\n\nclass {model.__name__}(BaseModel):\n"

  yaml_example = ""
  for attr, prop in model.model_json_schema()["properties"].items():
    yaml_example += f"\n{attr}: ..."

    if 'type' in prop and prop["type"] == "array":
      ret += f"{TAB}{attr}: list[{prop['items']['type']}] = Field(desc='{prop['desc']}', max_length={prop['maxItems']})\n"
    elif 'anyOf' in prop:
      ret += f"{TAB}{attr}: {' | '.join([x['type'] for x in prop['anyOf']])} = Field(desc='{prop['desc']}'"
    else:
      ret += f"{TAB}{attr}: {prop['type']} = Field(desc='{prop['desc']}')\n"

  ret += f"```\n\nYAML should be enclosed in triple backticks like\n```yaml{yaml_example}\n```\n"
  return ret


def parse_llm_response(model: type[BaseModel], llm_res: str):
  ptrn = re.compile(r"```yaml(.*?)```", re.DOTALL)
  match = re.search(ptrn, llm_res)
  if match:
    try:
      res_dict = yaml.safe_load(match.group(1))
      if isinstance(res_dict, dict): ret = model.model_validate(res_dict)
      elif isinstance(res_dict, list): ret = [model.model_validate(x) for x in res_dict]
      else: raise Exception(f"Shouldn't have reached here. Expected type of dict or list, but got {type(res_dict)}")
      return ret

    except ValidationError as e:
      print("Pydantic Validation Error:", e)
      print(llm_res)
    except yaml.YAMLError as e:
      print("YAML parsing error:", e)
      print(llm_res)
    except Exception as e:
      print("Error:", e)
      print(llm_res)
  else:
    print("Couldn't find yaml tags\nResponse:")
    print(llm_res)

  return None


def run(model: str, messages: list[Message], max_retries: int, response_model: Optional[type(BaseModel)] = None, temp: float = None):
  #messages[0].content += f"\n---\n\n{generate_response_prompt(response_model)}---\n"
  suffix = f"\n---\n\n{generate_response_prompt(response_model)}---\n"
  if dataclasses.is_dataclass(messages[-1]):
    messages[-1].content += suffix
  else:
    if isinstance(messages[-1]['content'], str):
      messages[-1]["content"] += suffix
    else:
      for x in messages[-1]["content"]:
        if x["type"] == "text":
          x["text"] += suffix
          break
      else:
        raise ValueError("Couldn't find text type in the last message")
  while max_retries:
    res = llm_call(model, messages, temp)
    ret = parse_llm_response(response_model, res)
    if ret is None: max_retries -= 1
    else: return ret
