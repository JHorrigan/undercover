import { useState } from "react";
import type { Run, Todo } from "./api";
import { api, errorMessage } from "./api";
import { TODO_LABEL, TODO_STATUSES } from "./format";
import { useData } from "./hooks";

const REFRESH_MS = 3000;
const DEFAULT_CAP = 5;

/** The agent's run over the queue: start one, then watch its to-do list. */
export function RunPanel() {
  const { data: run, error, reload } = useData(api.latestRun, REFRESH_MS);
  const running = Boolean(run && !run.finished_at);
  return (
    <section className="panel run" aria-label="Agent run">
      <div className="run-head">
        <div>
          <h2>{running ? "The agent is working the queue" : "Agent run"}</h2>
          {run && <RunMeta run={run} running={running} />}
        </div>
        {!running && <StartRun onStarted={reload} />}
      </div>
      {error && <p className="error">Couldn't load the run: {error}</p>}
      {run && <TodoList todos={run.todos} />}
      {run?.summary && (
        <blockquote className="summary">{run.summary}</blockquote>
      )}
    </section>
  );
}

function RunMeta({ run, running }: Readonly<{ run: Run; running: boolean }>) {
  const done = run.todos.filter((t) => t.status === "done").length;
  return (
    <p className="muted">
      <span className="mono">{run.run_id}</span>, capped at {run.cap}{" "}
      {run.cap === 1 ? "claim" : "claims"}
      {run.todos.length > 0 && (
        <>
          , {done} of {run.todos.length} done
        </>
      )}
      {!running && ", finished"}
    </p>
  );
}

function StartRun({ onStarted }: Readonly<{ onStarted: () => void }>) {
  const [cap, setCap] = useState(DEFAULT_CAP);
  const [error, setError] = useState<string>();
  const start = () => {
    api.startRun(cap).then(onStarted, (reason: unknown) => {
      setError(errorMessage(reason));
    });
  };
  return (
    <div className="start-run">
      <label htmlFor="cap">Claims to work</label>
      <input
        id="cap"
        type="number"
        min={1}
        max={25}
        value={cap}
        onChange={(event) => {
          setCap(Number(event.target.value));
        }}
      />
      <button
        type="button"
        className="primary"
        disabled={cap < 1}
        onClick={start}
      >
        Run the queue
      </button>
      {error && <p className="error">{error}</p>}
    </div>
  );
}

/** The run's to-do list, with a strip showing how far it has got. */
export function TodoList({ todos }: Readonly<{ todos: Todo[] }>) {
  if (todos.length === 0) {
    return <p className="muted">The agent's to-do list appears here.</p>;
  }
  const ordered = TODO_STATUSES.flatMap((s) =>
    todos.filter((t) => t.status === s),
  );
  return (
    <>
      <div className="todo-strip" aria-hidden="true">
        {ordered.map((todo) => (
          <span key={todo.text} className={`todo-${todo.status}`} />
        ))}
      </div>
      <ol className="todos" aria-label="The agent's to-do list">
        {todos.map((todo) => (
          <li key={todo.text} className={`todo todo-item-${todo.status}`}>
            <span className={`badge todo-${todo.status}`}>
              {TODO_LABEL[todo.status]}
            </span>
            <span className="todo-text">{todo.text}</span>
          </li>
        ))}
      </ol>
    </>
  );
}
