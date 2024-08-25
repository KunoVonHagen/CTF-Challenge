#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <openssl/hmac.h>

#define EMAIL_SIZE 256

void get_email(char *email) {
    char buffer[EMAIL_SIZE];  // This buffer is vulnerable to overflow
    
    printf("Saving email at %p\n", &buffer);
    printf("Enter your email: ");
    // Vulnerable to buffer overflow
    gets(buffer);  // Using gets() is inherently unsafe

    // Copy the email into the provided buffer
    strncpy(email, buffer, EMAIL_SIZE - 1);
    email[EMAIL_SIZE - 1] = '\0';  // Ensure null termination
}

void gen_flag(const char* secret, const char* user, char* result) {
    unsigned char* digest;
    unsigned int len = 32; // SHA256 produces a 32-byte hash

    // Create an HMAC_CTX pointer
    HMAC_CTX* ctx = HMAC_CTX_new();
    
    // Initialize the HMAC context with the secret and SHA256
    HMAC_Init_ex(ctx, secret, strlen(secret), EVP_sha256(), NULL);
    
    // Provide the message data to the HMAC context
    HMAC_Update(ctx, (unsigned char*)user, strlen(user));
    
    // Allocate memory for the digest
    digest = (unsigned char*)malloc(len);

    // Finalize the HMAC and retrieve the digest
    HMAC_Final(ctx, digest, &len);

    // Convert the digest to a hexadecimal string
    char hexdigest[65];
    for (int i = 0; i < len; i++) {
        sprintf(&hexdigest[i * 2], "%02x", digest[i]);
    }

    // Format the final flag string
    sprintf(result, "FLAG{%s}", hexdigest);

    // Clean up
    HMAC_CTX_free(ctx);
    free(digest);
}

int main() {
    uid_t original_uid = getuid();
    setuid(0);  // Elevate to root

    char secret1[256], secret2[256];
    char email[EMAIL_SIZE];
    char flag_output[256];
    FILE *file;

    // Read secret1.txt
    file = fopen("/root/secret1.txt", "r");
    if (file == NULL) {
        perror("Failed to open secret1.txt");
        exit(1);
    }
    fgets(secret1, sizeof(secret1), file);
    fclose(file);

    if (original_uid == 0) {
        // Read secret2.txt
        file = fopen("/root/secret2.txt", "r");
        if (file == NULL) {
            perror("Failed to open secret2.txt");
            exit(1);
        }
        fgets(secret2, sizeof(secret2), file);
        fclose(file);
    }

    // Get email from user
    get_email(email);

    gen_flag(secret1, email, flag_output);
    printf("flag1: %s\n", flag_output);

    if (original_uid == 0) {
        gen_flag(secret1, email, flag_output);
        printf("flag2: %s\n", flag_output);
    } else {
        printf("flag2: Permission denied\n");
    }

    setuid(original_uid);  // Reset UID to original
    return 0;
}
