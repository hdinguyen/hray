import { ActionPanel, Detail, LaunchProps, Action, getPreferenceValues } from "@raycast/api";
import { useState, useEffect } from "react";
import fetch from "node-fetch";

interface CommandArguments {
  question: string;
}

interface Preferences {
  host: string;
  apiKey?: string;
}

export default function Command(props: LaunchProps<{ arguments: CommandArguments }>) {
  const { question } = props.arguments;
  const { host, apiKey } = getPreferenceValues<Preferences>();
  const [isLoading, setIsLoading] = useState(true);
  const [data, setData] = useState("");

  const headers: HeadersInit = {
    'Content-Type': 'application/json'
  };
  
  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`;
  }

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch(`${host}/llm/quick_reply?msg=${encodeURIComponent(question)}`, {
          headers
        });
        const result = await response.text();
        const formattedResult = result.replace(/^"|"$/g, '').replace(/\\n/g, '\n');
        console.log(result);
        console.log(formattedResult);
        setData(formattedResult);
      } finally {
        setIsLoading(false);
      }
    }
    fetchData();
  }, [question, host]);
  
  return (
    <Detail
      markdown={data}
      isLoading={isLoading}
      navigationTitle={question}
      actions={
        <ActionPanel>
          <Action
            title="👍 Helpful"
            onAction={() => {
              // Send feedback that response was helpful
              fetch(`${host}/llm/feedback`, {
                method: "POST",
                body: JSON.stringify({ helpful: true, question, response: data })
              });
            }}
          />
          <Action
            title="👎 Not Helpful" 
            onAction={() => {
              // Send feedback that response was not helpful
              fetch(`${host}/llm/feedback`, {
                method: "POST",
                body: JSON.stringify({ helpful: false, question, response: data })
              });
            }}
          />
          <Action.OpenInBrowser
            title="Close Without Feedback"
            url="raycast://pop"
            onOpen={() => {
              // User closed without giving feedback
              fetch(`${host}/llm/feedback`, {
                method: "POST", 
                body: JSON.stringify({ helpful: null, question, response: data })
              });
            }}
          />
          <Action.OpenInBrowser
            title="Edit Question"
            url="raycast://pop"
            onOpen={() => {
              // Reopen with edited question
              fetch(`${host}/llm/quick_reply?msg=${encodeURIComponent(question)}`);
            }}
          />
        </ActionPanel>
      }
    />
  );
}
