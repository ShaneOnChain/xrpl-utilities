# wallet_from_mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from xrpl.wallet import Wallet
from config import MNEMONIC

# Replace with your actual mnemonic phrase


# Generate seed from mnemonic
seed_bytes = Bip39SeedGenerator(MNEMONIC).Generate()

# Derive key pair using BIP44 standard for XRP
bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.RIPPLE)
bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)

# Extract private key in hexadecimal format
private_key = bip44_acc_ctx.PrivateKey().Raw().ToHex()
public_key = bip44_acc_ctx.PublicKey().RawCompressed().ToHex()

# Create XRPL wallet instance
wallet = Wallet(public_key=public_key ,private_key=private_key)

# Display wallet details
print("Classic Address:", wallet.classic_address)
print("Public Key:", wallet.public_key)
print("Private Key:", wallet.private_key)
