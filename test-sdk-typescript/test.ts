import { PIEE, PIEEAPIError } from "@piee/sdk";

const baseURL = process.env.PIEE_BASE_URL || "http://localhost:8000";
const apiKey = process.env.PIEE_API_KEY || "pk-test-key";

console.log(`Testing PIEE TypeScript SDK against ${baseURL}`);

const piee = new PIEE({
    baseURL,
    apiKey,
});

async function runTests() {
    try {
        console.log("\n--- 1. Testing Models List ---");
        const modelsResponse = await piee.models.list();
        console.log("Available models:", modelsResponse.data.map(m => m.id));

        console.log("\n--- 2. Testing Chat Completions ---");
        console.log("Requesting non-streaming completion...");
        const chatResponse = await piee.chat.completions.create({
            model: "openai/gpt-4o",
            messages: [{ role: "user", content: "Hello, how are you?" }]
        });
        console.log("Response:", chatResponse.choices[0].message.content);

        console.log("\nRequesting streaming completion...");
        const stream = piee.chat.completions.stream({
            model: "openai/gpt-4o",
            messages: [{ role: "user", content: "Write a short haiku about AI." }]
        });

        process.stdout.write("Streaming output: ");
        for await (const chunk of stream) {
            if (chunk.choices && chunk.choices[0].delta.content) {
                process.stdout.write(chunk.choices[0].delta.content);
            }
        }
        console.log("\n");

    } catch (error) {
        if (error instanceof PIEEAPIError) {
            console.error(`API Error [Status ${error.status}]: ${error.message}`);
        } else {
            console.error("Unexpected error:", error);
        }
    }
}

runTests().then(() => console.log("Tests complete!"));
