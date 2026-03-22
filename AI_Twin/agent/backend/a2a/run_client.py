# Copyright (c) 2026 PCL-CCNN
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from entry_agent import EntryAgent
import asyncio


async def main():
    #base_url = "http://192.168.193.12:30090?token=eyJhbGciOiJSUzI1NiIsImtpZCI6IjEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwOi8vMTkyLjE2OC4xOTMuMTI6MzExMTEiLCJzdWIiOiI3MDEzMzYwMCIsImF1ZCI6InVzZXJfYWdlbnQiLCJleHAiOjE3NjQwNjU2NzYsImlhdCI6MTc2NDA2MjA3NiwiYXV0aF90aW1lIjoxNzY0MDYyMDc2LCJub25jZSI6IjI5MWZjNDUyLWZhMzgtNGE0NS1hYTQzLWFiYjNjOTBhMzM4NyIsIm5hbWUiOiJtYXJrQDEyMyIsImVtYWlsIjoiMTIzNDU2Nzg5QHFxLmNvbSJ9.O0z9Ww6YBko40TLWfUf6o9v_b_XMVdVvLRcl0pIV88biGxCWW-UQ-1oRYqWzR2WNUZ_Aen1E99TQSpO8w9spVcYwfgF9w_tlSArU_bAQXEsSn-nieOqU5caAzl10c6KJeR3gNa7_-RtptE7StZfjsBtoX-3Mal441je4oHq2uMTGgf2QXw0nxz62cMiAjs3PH6wAyRSFlU9NWfszIDEXZBliGJ1qSNW419QkVlZTATTZhxa7M76urzy35qg_dbPZhcPMbe9v0hjjf-7Fk78EE1dmRns5Hcbf9pwdCRVuQXeOV8YPmVkpG4zAMV5tJw1pISAYfJBMGs7QZ7CIjFs5cw"
    base_url = "http://172.25.23.143:9090?token=eyJhbGciOiJSUzI1NiIsImtpZCI6IjEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwOi8vMTcyLjI1LjIxLjEyOTo1MDAwIiwic3ViIjoiNzAxMzM2MDAiLCJhdWQiOiJ1c2VyX2FnZW50IiwiZXhwIjoxNzY0NTU4NzY3LCJpYXQiOjE3NjQ1NTUxNjcsImF1dGhfdGltZSI6MTc2NDU1NTE2Nywibm9uY2UiOiI4MzE2ZmZjZS0yMmNmLTRjNGYtYjY5Ni03YTI2NzMzODk2ZDkiLCJuYW1lIjoibWFya0AxMjMiLCJlbWFpbCI6IjEyMzQ1Njc4OUBxcS5jb20ifQ.TsciRhGW4i0eHmdEpdN5u0fWNsyVWL0hNUIelqE4aKVVFOzLT0_U3c0FBxkMEGqr6qZ_PP8rbX0jfVWupQ6USvIBWIZaz__jhL93lOTUPLxEG7Cy_7dgonKzFkiJHoM2EKcvmiAmxWVW1NM7ePwf13WqdXrj03flGRJTW7YRBwTjL_Pton988OjiNfMIxazRqzeniSGNLIGxcvK_d2Wj72w7tsDl--HBlssyQ4mQPCmy_4WX1ocPejz14OR_t7JrECcugiYdhcqIe5Lk3Y6V8_LgTvSLxCima22tQXiMnXDabd48-habZO6iCpbnypQGiisEKQWAj86rrPYHxvP0Bw"
    entry_agent = EntryAgent()

    response = await entry_agent.invoke(
        base_url, prompt="内科"
    )
    
    print(response)


if __name__ == "__main__":

    asyncio.run(main())
