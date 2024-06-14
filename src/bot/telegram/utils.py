import urllib


def _prepare_twitter_link(invite_link: str) -> str:
    encoded_text = urllib.parse.quote(
        f"Get your early access to Moon 🌚 - Telegram Wallet for Solana Memecoins:\n{invite_link}"
    )

    return f"https://twitter.com/intent/tweet?text={encoded_text}"
