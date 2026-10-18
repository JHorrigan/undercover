import { useRoute } from "./hooks";
import { Queue } from "./Queue";

export function App() {
  const route = useRoute();
  return (
    <>
      <header className="topbar">
        <a className="wordmark" href="#/">
          UnderCover
        </a>
        <nav aria-label="Main">
          <a
            href="#/"
            aria-current={route.page === "queue" ? "page" : undefined}
          >
            Queue
          </a>
        </nav>
      </header>
      <main>
        <Queue />
      </main>
    </>
  );
}
