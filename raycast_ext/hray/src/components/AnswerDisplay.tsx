import { Form, ActionPanel, Action, Detail, Color } from "@raycast/api";

interface HistoryItem {
  helpful: boolean;
  id: number;
  question: string;
  created_at: string;
  response: string;
  ignore: boolean;
}

interface AnswerDisplayProps {
  question: string;
  onSubmit: (question: string) => void;
  data: string;
  isLoading: boolean;
  onHelpful: () => void;
  onNotHelpful: () => void;
  onClose: () => void;
  history?: HistoryItem[];
  placeholder?: string;
}

export function AnswerDisplay({
  question,
  onSubmit,
  data,
  isLoading,
  onHelpful,
  onNotHelpful,
  onClose,
  history = [],
  placeholder = "Ask a question..."
}: AnswerDisplayProps) {
  function handleSubmit(values: { question: string }) {
    console.log("handleSubmit", values);
    const trimmedQuestion = values.question.trim();
    if (trimmedQuestion) {
      onSubmit(trimmedQuestion);
    }
  }

  const latestHistoryItem = history[0];
  const showLatestHistory = !question && latestHistoryItem;
  const displayData = showLatestHistory ? latestHistoryItem.response : data;

  return (
    <Form
      actions={
        <ActionPanel>
          <Action.SubmitForm title={isLoading ? "Ask Another" : "Ask"} onSubmit={handleSubmit} />
          {!showLatestHistory && data && !isLoading && (
            <>
              <Action title="👍 Helpful" onAction={onHelpful} />
              <Action title="👎 Not Helpful" onAction={onNotHelpful} />
              <Action title="Close" onAction={onClose} />
            </>
          )}
        </ActionPanel>
      }
    >
      <Form.TextArea
        id="question"
        title="Question"
        placeholder={placeholder}
        defaultValue={question}
      />
      {(isLoading || displayData) && (
        <>
          {isLoading && (
            <Form.Description
              title="Loading..."
              text="Waiting for response..."
            />
          )}
          {displayData && !isLoading && (
            <Form.Description
              title="Answer"
              text={displayData}
            />
          )}
        </>
      )}
      {history.length > 0 && (
        <Form.Description
          title="Recent Questions"
          text={history.slice(0, 5).map((item) => 
            `${item.question} (${new Date(item.created_at).toLocaleString()}) ${
              item.helpful ? "👍" : item.ignore ? "🚫" : "👎"
            }`
          ).join("\n")}
        />
      )}
    </Form>
  );
} 