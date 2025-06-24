import "./App.css";
import AiChatbot from "./components/AiChatbot";
import { createBrowserRouter, RouterProvider } from "react-router";

function App() {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <div>Main page</div>,
    },
    {
      path: "/ai",
      element: <AiChatbot />,
    },
  ]);

  return (
    <>
      <RouterProvider router={router} />
    </>
  );
}

export default App;
