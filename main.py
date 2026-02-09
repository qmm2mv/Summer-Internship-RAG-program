import importlib
import time

#Function for getting user inputs
def get_interactive_args():
    print("Press Enter to skip and use the default values")
    query_text = input("Enter your prompt: ")
    num_chunks = int(input("Enter the number of chunks: ") or "5")
    model_name = input("Enter model name. Choices are phi3:mini, qwen2.5:0.5b, or anything you have installed on Ollama already. \n (default: phi3:mini): ") or "phi3:mini"
    output_file = input("Enter output file name (optional): ")
    context_length = int(input("Enter max context (default: 1000 words): ") or 1000)
    source_filter = input("Enter source filter (optional): ")
    show_chunks = input("Show chunks? true/false: ").lower() == "true"
    return {
        "query_text": query_text,
        "k": num_chunks,
        "model_name": model_name,
        "max_context_length": context_length,
        "source_filter": source_filter or None,
        "show_chunks": show_chunks,
        "output": output_file
    }

# --- MAIN ---
def main(cli_args=None):
    argparse = importlib.import_module("argparse")
    logging = importlib.import_module("logging")
    asyncio = importlib.import_module("asyncio")
    query = importlib.import_module("query")

    #parses arguments
    logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="Run RAG query via CLI or interactive mode.")
    parser.add_argument("--interactive", action="store_true", help="Use interactive input prompts")
    parser.add_argument("--query_text", type=str, help="Query text")
    parser.add_argument("--num_chunks", type=int, default=5, help="Number of chunks")
    parser.add_argument("--model", type=str, default="phi3:mini", help="Ollama model name")
    parser.add_argument("--output", type=str, help="Output file")
    parser.add_argument("--max_context", type=int, default=2000, help="Max token context")
    parser.add_argument("--source_filter", type=str, help="Filter by source")
    parser.add_argument("--show_chunks", action="store_true", help="Show chunk content")

    start = time.time()
    # Parse arguments from cli_args if provided, otherwise use sys.argv
    if cli_args is not None:
        args = parser.parse_args(cli_args)
    else:
        args = parser.parse_args()

    if args.interactive or not args.query_text:
        logging.info("Interactive mode enabled.")
        input_args = get_interactive_args()
    else:
        input_args = {
            "query_text": args.query_text,
            "k": args.num_chunks,
            "model_name": args.model,
            "max_context_length": args.max_context,
            "source_filter": args.source_filter,
            "show_chunks": args.show_chunks,
            "output": args.output
        }

    response = asyncio.run(query.query_rag(
        query_text=input_args["query_text"],
        k=input_args["k"],
        model_name=input_args["model_name"],
        max_context_length=input_args["max_context_length"],
        source_filter=input_args["source_filter"],
        show_chunks=input_args["show_chunks"]
    ))

    if response and input_args["output"]:
        try:
            with open(input_args["output"], "w", encoding="utf-8") as f:
                f.write(f"Query: {input_args['query_text']}Response:{response['text']}Sources:{response['sources']}")
            logging.info(f"Response saved to {input_args['output']}")
        except Exception as e:
            logging.error(f"Error writing output: {e}")

    print(f"\n⏱️ Total time: {time.time() - start:.2f} seconds")
    return response

if __name__ == "__main__":
   main()
