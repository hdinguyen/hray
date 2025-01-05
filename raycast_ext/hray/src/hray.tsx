import { ActionPanel, LaunchProps, getPreferenceValues, showToast } from "@raycast/api";
import { useState, useEffect } from "react";
import axios from "axios";
import { AnswerDisplay } from "./components/AnswerDisplay";

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

interface ApiResponse {
  status: string;
  display: string;
  data: string;
}

type ScreenProps = {
  data: string;
  isLoading: boolean;
  question: string;
  onHelpful?: () => Promise<void>;
  onNotHelpful?: () => Promise<void>;
  onClose?: () => void;
  onEdit?: () => void;
  onSubmit?: (question: string) => void;
};

const AnswerDisplayWrapper = (props: ScreenProps) => (
  <AnswerDisplay
    data={props.data}
    isLoading={props.isLoading}
    question={props.question}
    onHelpful={props.onHelpful || (() => Promise.resolve())}
    onNotHelpful={props.onNotHelpful || (() => Promise.resolve())}
    onClose={props.onClose || (() => {})}
    onEdit={props.onEdit || (() => {})}
    onSubmit={props.onSubmit || (() => {})}
  />
);

function makeRequest(endpoint: string, method: string = "GET", body?: RequestBody) {
  const { host, apiKey } = getPreferenceValues<Preferences>();

  console.log(host, apiKey);

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

const SCREEN_COMPONENTS: Record<string, React.ComponentType<ScreenProps>> = {
  'lack_context': AnswerDisplayWrapper,
  'default': AnswerDisplayWrapper,
};

export default function Command(props: LaunchProps<{ arguments: CommandArguments }>) {
  const { question } = props.arguments;
  const [isLoading, setIsLoading] = useState(true);
  const [data, setData] = useState("");
  const [displayType, setDisplayType] = useState<string>("loading");

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await makeRequest(`/llm/quick_reply?msg=${encodeURIComponent(question)}`);
        const formattedResult = response.data as ApiResponse;
        console.log(response.data);
        console.log(formattedResult);
        
        setDisplayType(formattedResult.display || "default");
        setData(formattedResult.data);
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
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

  const handleRetry = async (newQuestion: string) => {
    console.log("handleRetry", newQuestion);
    setIsLoading(true);
    setDisplayType("default");
    try {
      const response = await makeRequest(`/llm/quick_reply?msg=${encodeURIComponent(newQuestion)}`);
      const formattedResult = response.data as ApiResponse;
      setDisplayType(formattedResult.display || "default");
      setData(formattedResult.data);
    } finally {
      setIsLoading(false);
    }
  };

  const ScreenComponent = SCREEN_COMPONENTS[displayType] || SCREEN_COMPONENTS.default;
  const screenProps: ScreenProps = {
    data,
    isLoading,
    question,
    ...(displayType === 'lack_context' 
      ? { onSubmit: handleRetry }
      : {
          onSubmit: handleRetry,
          onHelpful: handleHelpful,
          onNotHelpful: handleNotHelpful,
          onClose: handleClose,
          onEdit: handleEdit,
        }
    ),
  };

  return <ScreenComponent {...screenProps} />;
}
