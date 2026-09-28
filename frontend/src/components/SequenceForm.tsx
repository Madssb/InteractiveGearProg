import getSequenceFromInput from "@/chartbuilder/sequenceFromInput";
import getStringifiedSequence from "@/chartbuilder/stringifySequence";
import React, { useState } from "react";
import "@/styles/SequenceForm.css";

type SequenceFormProps = {
  setMilestoneSequence: React.Dispatch<React.SetStateAction<string[][]>>;
  initialSequence: string[][];
};

function InvalidFormat() {
  return (
    <div className="format-error">
      <div className="wrapper">
        <div className="header">Invalid input format used. Valid examples:</div>
          <div className="example-table">
            <div className="row">
              <div className="bold"> JSON:</div>
              <div className="code">[["rotten tomato", "dusty key"], ["skull", "strange object"], ["dirty blast"]]</div>
            </div>
            <div className="row">
              <div className="bold">Unquoted pseudo-JSON: </div>
              <div className="code">[[rotten tomato, dusty key], [skull, strange object], [dirty blast]]</div>
            </div>
            <div className="row">
              <div className="bold">Lazy quoted: </div>
              <div className="code">["rotten tomato", "dusty key"], ["skull", "strange object"], ["dirty blast"]</div>
            </div>
            <div className="row">
              <div className="bold">Lazy unquoted: </div>
              <div className="code">[rotten tomato, dusty key], [skull, strange object], [dirty blast]</div>
            </div>
          </div>
        </div>
      </div>
  )
}


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
  const [formatErr, setFormatErr] = useState(false);
  /**
   * Parses, normalizes, stores, then fetches metadata for new items.
   * Any thrown errors become inline messages under the form.
   */
  function handleSubmit(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      const sequenceAndFormat = getSequenceFromInput(inputText);
      setMilestoneSequence(sequenceAndFormat.sequence);
      setQuotes(sequenceAndFormat.quotes);
      setMultiline(inputText.trim().includes("\n"));
      setInputText(
        getStringifiedSequence(sequenceAndFormat.sequence, quotes, multiline),
      );
      setFormatErr(false);
    } catch {
      setFormatErr(true);
    }
    
  }

  const style: React.CSSProperties = {
    display: "flex",
    width: "100%",
    flexDirection: "column",
  };
  const examples: string[] = [
    '[["abyssal whip"], ["cake", "rune scimitar"]]',
    '["abyssal whip"], ["cake", "rune scimitar"]',
    '[[abyssal whip], [cake, rune scimitar]]',
    '[abyssal whip], [cake, rune scimitar]',

  ]
  const exampleStr = "Examples:\n\t" + examples.join("\n\t")
  return (
    <>
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
          placeholder={exampleStr}
        ></textarea>
        <input type="submit" value="Submit" />
      </form>
      {formatErr && (
        <InvalidFormat />
      )}
  </>
  );
}
