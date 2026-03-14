import asyncio
import httpx

async def main():
    base_url = "https://figgier-uninstructively-novella.ngrok-free.dev"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{base_url}/")
            print("Status code:", resp.status_code)
            print("Response:", resp.text)
            
            resp2 = await client.get(f"{base_url}/api/tags")
            print("Tags status:", resp2.status_code)
            print("Tags response:", resp2.text)
    except Exception as e:
        print("Exception:", str(e))

asyncio.run(main())
