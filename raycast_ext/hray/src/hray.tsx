import { ActionPanel, LaunchProps, getPreferenceValues, showToast } from "@raycast/api";
import { useState, useEffect } from "react";
import axios from "axios";
import { QuestionDetail } from "./components/QuestionDetail";

interface CommandArguments {
  question: string;
}

interface Preferences {
  host: string;
  apiKey?: string;
}

interface RequestBody {
  helpful?: boolean | null;
  question?: string;
  response?: string;
}

function makeRequest(endpoint: string, method: string = "GET", body?: RequestBody) {
  const { host, apiKey } = getPreferenceValues<Preferences>();
  
  return axios({
    url: `${host}${endpoint}`,
    method,
    data: body,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKey || "M3rryChr!stm@s",
    }
  });
}

export default function Command(props: LaunchProps<{ arguments: CommandArguments }>) {
  const { question } = props.arguments;
  const [isLoading, setIsLoading] = useState(true);
  const [data, setData] = useState("");

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await makeRequest(`/llm/quick_reply?msg=${encodeURIComponent(question)}`);
        const formattedResult = response.data.replace(/^"|"$/g, "").replace(/\\n/g, "\n");
        console.log(response.data);
        console.log(formattedResult);
        setData(formattedResult);
      } finally {
        setIsLoading(false);
      }
    }
    const interval = setInterval(() => {
      setData("🤔" + ".".repeat((Date.now() / 500) % 4) + " !");
    }, 500);

    fetchData().finally(() => {
      clearInterval(interval);
    });
  }, [question]);

  const handleHelpful = async () => {
    await makeRequest("/llm/feedback", "POST", { helpful: true, question, response: data });
    await showToast({ title: "Noted to learn" });
  };

  const handleNotHelpful = async () => {
    await makeRequest("/llm/feedback", "POST", { helpful: false, question, response: data });
    await showToast({ title: "Noted to learn" });
  };

  const handleClose = () => {
    makeRequest("/llm/feedback", "POST", { helpful: null, question, response: data });
  };

  const handleEdit = () => {
    makeRequest(`/llm/quick_reply?msg=${encodeURIComponent(question)}`);
  };

  return (
    <QuestionDetail
      data={data}
      isLoading={isLoading}
      question={question}
      onHelpful={handleHelpful}
      onNotHelpful={handleNotHelpful}
      onClose={handleClose}
      onEdit={handleEdit}
    />
  );
}
