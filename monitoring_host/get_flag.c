#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <openssl/hmac.h>

void gen_flag(const char* secret, const char* user, char* result) {
    unsigned char* digest;
    unsigned int len = 32; // SHA256 produces a 32-byte hash

    // Create an HMAC_CTX variable
    HMAC_CTX ctx;
    
    // Initialize the HMAC context
    HMAC_CTX_init(&ctx);

    // Initialize the HMAC context with the secret and SHA256
    HMAC_Init_ex(&ctx, secret, strlen(secret), EVP_sha256(), NULL);
    
    // Provide the message data to the HMAC context
    HMAC_Update(&ctx, (unsigned char*)user, strlen(user));
    
    // Allocate memory for the digest
    digest = (unsigned char*)malloc(len);

    // Finalize the HMAC and retrieve the digest
    HMAC_Final(&ctx, digest, &len);

    // Convert the digest to a hexadecimal string
    char hexdigest[65];
    for (int i = 0; i < len; i++) {
        sprintf(&hexdigest[i * 2], "%02x", digest[i]);
    }

    // Format the final flag string
    sprintf(result, "FLAG{%s}", hexdigest);

    // Clean up
    HMAC_CTX_cleanup(&ctx);
    free(digest);
}

int main() {
    char result[256];
    char user[256];
    char secret[256];

    // Prompt the user for their email
    printf("Enter your email: ");
    if (!fgets(user, sizeof(user), stdin)) {
        fprintf(stderr, "Error reading email.\n");
        return 1;
    }

    // Remove newline character if present
    size_t user_len = strlen(user);
    if (user[user_len - 1] == '\n') {
        user[user_len - 1] = '\0';
    }

    // Open the secret file
    FILE* secret_file = fopen("secret.txt", "r");
    if (!secret_file) {
        perror("Error opening secret file");
        return 1;
    }

    // Read the secret from the file
    if (!fgets(secret, sizeof(secret), secret_file)) {
        perror("Error reading secret file");
        fclose(secret_file);
        return 1;
    }
    fclose(secret_file);

    // Remove newline character if present
    size_t secret_len = strlen(secret);
    if (secret[secret_len - 1] == '\n') {
        secret[secret_len - 1] = '\0';
    }

    gen_flag(secret, user, result);
    printf("%s\n", result);
    return 0;
}
