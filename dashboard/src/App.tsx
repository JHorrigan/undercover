import { useSyncExternalStore } from "react";
import { Claim } from "./Claim";
import { Instructions } from "./Instructions";
import { Queue } from "./Queue";
import { useTheme } from "./theme";

function subscribe(onChange: () => void) {
  window.addEventListener("hashchange", onChange);
  return () => {
    window.removeEventListener("hashchange", onChange);
  };
}

function useHash(): string {
  return useSyncExternalStore(subscribe, () => window.location.hash);
}

function Page({ hash }: Readonly<{ hash: string }>) {
  const claim = /^#\/claims\/([\w-]+)$/.exec(hash);
  if (claim) return <Claim key={claim[1]} id={claim[1]} />;
  if (hash === "#/instructions") return <Instructions />;
  return <Queue />;
}

/** The dashboard: the header, and the page the address points to. */
export function App() {
  const hash = useHash();
  const { theme, toggle } = useTheme();
  const onInstructions = hash === "#/instructions";

  return (
    <div className="shell">
      <header className="topbar">
        <a className="brand" href="#/">
          UnderCover
        </a>
        <nav aria-label="Main">
          <a href="#/" aria-current={onInstructions ? undefined : "page"}>
            Claims
          </a>
          <a
            href="#/instructions"
            aria-current={onInstructions ? "page" : undefined}
          >
            Instructions
          </a>
        </nav>
        <button className="button button-quiet" type="button" onClick={toggle}>
          {theme === "dark" ? "Light mode" : "Dark mode"}
        </button>
      </header>
      <main>
        <Page hash={hash} />
      </main>
    </div>
  );
}
