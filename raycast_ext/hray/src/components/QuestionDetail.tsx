import { Detail, ActionPanel, Action } from "@raycast/api";

interface QuestionDetailProps {
  data: string;
  isLoading: boolean;
  question: string;
  onHelpful: () => void;
  onNotHelpful: () => void;
  onClose: () => void;
  onEdit: () => void;
}

export function QuestionDetail({
  data,
  isLoading,
  question,
  onHelpful,
  onNotHelpful,
  onClose,
  onEdit,
}: QuestionDetailProps) {
  return (
    <Detail
      markdown={data}
      isLoading={isLoading}
      navigationTitle={question}
      actions={
        <ActionPanel>
          <Action title="👍 Helpful" onAction={onHelpful} />
          <Action title="👎 Not Helpful" onAction={onNotHelpful} />
          <Action title="✏️ Edit" onAction={onEdit} />
          <Action title="Close" onAction={onClose} />
        </ActionPanel>
      }
    />
  );
} 