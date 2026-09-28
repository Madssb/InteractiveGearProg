import getSequenceFromInput from "@/chartbuilder/sequenceFromInput";
import getStringifiedSequence from "@/chartbuilder/stringifySequence";
import React, { useState } from "react";

type SequenceFormProps = {
  setMilestoneSequence: React.Dispatch<React.SetStateAction<string[][]>>;
  initialSequence: string[][];
};

/**
 * Form component for user-submitted sequence.
 */
export default function SequenceForm({
  setMilestoneSequence,
  initialSequence,
}: SequenceFormProps) {
  const [quotes, setQuotes] = useState(false);
  const [multiline, setMultiline] = useState(true);
  const [inputText, setInputText] = useState(() =>
    getStringifiedSequence(initialSequence, quotes, multiline),
  );

  /**
   * Keep focus inside the textarea on Tab and insert a literal tab character.
   */
  function handleTextareaKeyDown(
    e: React.KeyboardEvent<HTMLTextAreaElement>,
  ) {
    if (e.key !== "Tab") return;
    e.preventDefault();
    const textarea = e.currentTarget;
    const { selectionStart, selectionEnd, value } = textarea;
    const nextValue = `${value.slice(0, selectionStart)}\t${value.slice(selectionEnd)}`;
    setInputText(nextValue);

    // Restore cursor to after inserted tab.
    requestAnimationFrame(() => {
      textarea.selectionStart = selectionStart + 1;
      textarea.selectionEnd = selectionStart + 1;
    });
  }

  /**
   * Parses, normalizes, stores, then fetches metadata for new items.
   * Any thrown errors become inline messages under the form.
   */
  function handleSubmit(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault();
    const sequenceAndFormat = getSequenceFromInput(inputText);
    setMilestoneSequence(sequenceAndFormat.sequence);
    setQuotes(sequenceAndFormat.quotes);
    setMultiline(inputText.trim().includes("\n"));
    setInputText(
      getStringifiedSequence(sequenceAndFormat.sequence, quotes, multiline),
    );
  }

  const style: React.CSSProperties = {
    display: "flex",
    width: "100%",
    flexDirection: "column",
  };
  return (
    <form onSubmit={handleSubmit} style={style}>
      <label htmlFor="sequence">Sequence:</label>
      <textarea
        id="sequence"
        className="sequence"
        rows={10}
        style={{ width: "100%", tabSize: 2 }}
        autoComplete="off"
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        onKeyDown={handleTextareaKeyDown}
        placeholder={`Examples:\n"abyssal whip", ["cake", "rune scimitar"], "dragon bones"\nabyssal whip, [cake, rune scimitar], dragon bones\n[["abyssal whip"], ["cake", "rune scimitar"], ["dragon bones"]]`}
      ></textarea>
      <input type="submit" value="Submit" />
    </form>
  );
}
