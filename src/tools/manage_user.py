import argparse
import asyncio
from src.database.db import db_manager, VALID_KEY_PROVIDERS
from src.config import SUPPORTED_PROVIDERS


async def list_users() -> None:
    await db_manager.init_db()
    import aiosqlite
    async with aiosqlite.connect(db_manager.db_path) as db:
        async with db.execute("SELECT user_id, target_language, selected_provider, updated_at FROM user_settings") as cursor:
            rows = await cursor.fetchall()
            if not rows:
                print("No users found in database.")
                return
            print("=" * 60)
            print(f"{'User ID':<15} {'Target Lang':<15} {'Provider':<18} {'Last Updated'}")
            print("=" * 60)
            for row in rows:
                print(f"{row[0]:<15} {row[1]:<15} {row[2]:<18} {row[3]}")
            print("=" * 60)


async def set_user_key(user_id: int, provider: str, api_key: str) -> None:
    await db_manager.init_db()
    if provider not in VALID_KEY_PROVIDERS:
        print(f"Error: Invalid provider '{provider}'. Valid options: {VALID_KEY_PROVIDERS}")
        return
    await db_manager.set_user_api_key(user_id, provider, api_key)
    masked = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
    print(f"Successfully set custom '{provider}' key for User ID {user_id}: {masked}")


async def delete_user_key(user_id: int, provider: str) -> None:
    await db_manager.init_db()
    await db_manager.delete_user_api_key(user_id, provider)
    print(f"Successfully deleted '{provider}' key for User ID {user_id}.")


async def set_user_preferences(user_id: int, target_lang: str = None, provider: str = None) -> None:
    await db_manager.init_db()
    if target_lang:
        await db_manager.set_target_language(user_id, target_lang)
        print(f"Set target language for User ID {user_id} -> {target_lang}")
    if provider:
        if provider not in SUPPORTED_PROVIDERS:
            print(f"Error: Unsupported provider '{provider}'. Options: {SUPPORTED_PROVIDERS}")
            return
        await db_manager.set_user_provider(user_id, provider)
        print(f"Set provider for User ID {user_id} -> {provider}")


def main():
    parser = argparse.ArgumentParser(description="CLI Tool to manage bot users and API keys")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List all registered users and their settings")

    # set-key
    p_set_key = subparsers.add_parser("set-key", help="Assign a custom API key to a specific user")
    p_set_key.add_argument("--user-id", type=int, required=True, help="Telegram User ID")
    p_set_key.add_argument("--provider", type=str, required=True, help="Provider name (openrouter, deepl, etc.)")
    p_set_key.add_argument("--key", type=str, required=True, help="API Key value")

    # delete-key
    p_del_key = subparsers.add_parser("delete-key", help="Delete custom API key of a user")
    p_del_key.add_argument("--user-id", type=int, required=True, help="Telegram User ID")
    p_del_key.add_argument("--provider", type=str, required=True, help="Provider name")

    # set-settings
    p_set_pref = subparsers.add_parser("set-settings", help="Set user target language or active provider")
    p_set_pref.add_argument("--user-id", type=int, required=True, help="Telegram User ID")
    p_set_pref.add_argument("--target-lang", type=str, help="Target language")
    p_set_pref.add_argument("--provider", type=str, help="Provider name")

    args = parser.parse_args()

    if args.command == "list":
        asyncio.run(list_users())
    elif args.command == "set-key":
        asyncio.run(set_user_key(args.user_id, args.provider, args.key))
    elif args.command == "delete-key":
        asyncio.run(delete_user_key(args.user_id, args.provider))
    elif args.command == "set-settings":
        asyncio.run(set_user_preferences(args.user_id, args.target_lang, args.provider))


if __name__ == "__main__":
    main()
