import itertools
import hmac
import hashlib
import base64
import time
import sys
import argparse

# Banner Function to print banner like metasploit
def print_banner():
    banner = """
    *****************************************************************************************************************************
    *      8M:::::::8888M:::::888:::::::88:::8888888::::::::Mm                                                                  *
    *    88MM:::::8888M:::::::88::::::::8:::::888888:::M:::::M                                                                  *
    *   8888M:::::888MM::::::::8:::::::::::M::::8888::::M::::M                                                                  *
    *  88888M:::::88:M::::::::::8:::::::::::M:::8888::::::M::M  Token Brute-Forcer (by MrSET)                                   * 
    *  88 888MM:::888:M:::::::::::::::::::::::M:8888:::::::::M:                                                                 *                      
    *  8 88888M:::88::M:::::::::::::::::::::::MM:88::::::::::::M        A Python tool to brute-force token                      *
    *   88888M:::88::M::::::::::*88*::::::::::M:88::::::::::::::M                                                               *
    *  888888M:::88::M:::::::::88@@88:::::::::M::88::::::::::::::M     Signatures using wordlist or brute-force.                *
    *  888888MM::88::MM::::::::88@@88:::::::::M:::8::::::::::::::*8                                                             *       
    *  88888  M:::8::MM:::::::::*88*::::::::::M:::::::::::::::::88@@   linkedin.com/mohamed-ali-ayadi                           *
    *  8888   MM::::::MM:::::::::::::::::::::MM:::::::::::::::::88@@                                                            *
    *  888    M:::::::MM:::::::::::::::::::MM::M::::::::::::::::*8    that's take a long time here some nudes to watch ... xD   *
    *  888    MM:::::::MMM::::::::::::::::MM:::MM:::::::::::::::M                                                               *                    
    *   88     M::::::::MMMM:::::::::::MMMM:::::MM::::::::::::MM     Good Hunting!                                              *
    *    88    MM:::::::::MMMMMMMMMMMMMMM::::::::MMM::::::::MMM                                                                 *
    *     88    MM::::::::::::MMMMMMM::::::::::::::MMMMMMMMMM      MrSET - 2024                                                 *
    *      88   8MM::::::::::::::::::::::::::::::::::MMMMMM                                                                     *
    *****************************************************************************************************************************
    """
    print(banner)

# Function to compute the signature
def compute_signature(secret_key, header, payload):
    computed_signature = hmac.new(
        secret_key.encode(), f"{header}.{payload}".encode(), hashlib.sha256
    ).digest()
    return base64.urlsafe_b64encode(computed_signature).decode().rstrip("=")

# Brute-force keys using wordlist first, then fall back to brute-force
def brute_force_key(charset, key_length_range, wordlist_path, token_header, token_payload, token_signature):
    attempt_counter = 0  # Counter for attempts
    start_time = time.time()  # Record start time
    charset_size = len(charset)

    # Try the wordlist first
    with open(wordlist_path, 'r') as wordlist:
        for word in wordlist:
            key = word.strip()  # Remove any extra whitespace or newline characters
            attempt_counter += 1

            # Compute signature
            if compute_signature(key, token_header, token_payload) == token_signature:
                elapsed_time = time.time() - start_time
                sys.stdout.write(f"\rKey found from wordlist: {key} | Total attempts: {attempt_counter} | Time taken: {elapsed_time / 60:.2f} minutes\n")
                return key

            # Progress update for wordlist attempts
            if attempt_counter % 1000 == 0:
                elapsed_time = time.time() - start_time
                avg_time_per_attempt = elapsed_time / attempt_counter
                time_spent_minutes = elapsed_time / 60
                sys.stdout.write(f"\rWordlist: Attempts so far: {attempt_counter} | Time spent: {time_spent_minutes:.2f} minutes")
                sys.stdout.flush()

    # If wordlist doesn't find the key, fall back to brute-force
    sys.stdout.write("\rWordlist exhausted. Falling back to brute-force...\n")

    # Brute-force using the charset if the wordlist didn't find the key
    for key_length in key_length_range:
        total_combinations = charset_size ** key_length  # Calculate total combinations
        sys.stdout.write(f"Trying keys of length {key_length} ({total_combinations} combinations)...\n")
        
        for key in itertools.product(charset, repeat=key_length):
            key = "".join(key)
            attempt_counter += 1

            # Compute signature
            if compute_signature(key, token_header, token_payload) == token_signature:
                elapsed_time = time.time() - start_time
                sys.stdout.write(f"\rKey found: {key} | Total attempts: {attempt_counter} | Time taken: {elapsed_time / 60:.2f} minutes\n")
                return key

            # Progress update every 100,000 attempts
            if attempt_counter % 100000 == 0:
                elapsed_time = time.time() - start_time
                avg_time_per_attempt = elapsed_time / attempt_counter
                total_time_seconds = total_combinations * avg_time_per_attempt
                total_time_minutes = total_time_seconds / 60
                time_spent_minutes = elapsed_time / 60
                time_remaining_minutes = total_time_minutes - time_spent_minutes

                # Calculate percentage
                percentage = (attempt_counter / total_combinations) * 100

                # Print the progress
                sys.stdout.write(f"\rTesting key: {key} | Attempts: {attempt_counter} | "
                                 f"Progress: {percentage:.2f}% | Time spent: {time_spent_minutes:.2f} minutes | "
                                 f"Estimated total time: {total_time_minutes:.2f} minutes | "
                                 f"Estimated time remaining: {time_remaining_minutes:.2f} minutes")
                sys.stdout.flush()  # Make sure output is updated

    sys.stdout.write("\rKey not found.\n")
    return None

# Command-line argument parsing
def parse_args():
    parser = argparse.ArgumentParser(description="Brute-force token signature or try from wordlist.")
    parser.add_argument("token", help="The full token (header.payload.signature)")
    parser.add_argument("wordlist", help="Path to the wordlist file for brute-force")
    return parser.parse_args()

# Main execution
if __name__ == "__main__":
    # Print the banner
    print_banner()

    # Parse command-line arguments
    args = parse_args()

    # Split the token into its components
    token_parts = args.token.split(".")
    if len(token_parts) != 3:
        print("Invalid token format. Make sure it's in the format: header.payload.signature")
        sys.exit(1)

    header = token_parts[0]
    payload = token_parts[1]
    signature = token_parts[2]

    # Define character set (A-Z, a-z, 0-9)
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

    # Define key length range (example: start with 5 characters, up to 32)
    key_length_range = range(5, 33)

    # Run the brute-force attack with wordlist first, then brute-force
    key = brute_force_key(charset, key_length_range, args.wordlist, header, payload, signature)
