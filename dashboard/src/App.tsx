import { ClaimPage } from "./ClaimPage";
import type { Route } from "./hooks";
import { useRoute } from "./hooks";
import { Instructions } from "./Instructions";
import { Queue } from "./Queue";

function Page({ route }: Readonly<{ route: Route }>) {
  if (route.page === "claim") return <ClaimPage key={route.id} id={route.id} />;
  if (route.page === "instructions") return <Instructions />;
  return <Queue />;
}

export function App() {
  const route = useRoute();
  const current = (page: Route["page"]) =>
    route.page === page ? "page" : undefined;
  return (
    <>
      <header className="topbar">
        <a className="wordmark" href="#/">
          UnderCover
        </a>
        <nav aria-label="Main">
          <a href="#/" aria-current={current("queue")}>
            Queue
          </a>
          <a href="#/instructions" aria-current={current("instructions")}>
            Instructions
          </a>
        </nav>
      </header>
      <main>
        <Page route={route} />
      </main>
    </>
  );
}
