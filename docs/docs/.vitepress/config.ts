export default {
  title: "Streamsync",
  description:
    "Create data apps using a drag-and-drop UI editor, while retaining the full power of Python in the backend.",
  themeConfig: {
    logo: "/logo.svg",
    socialLinks: [
      {
        icon: "github",
        link: "https://github.com/streamsync-cloud/streamsync",
      },
    ],
    nav: [
      { text: "Documentation", link: "/getting-started" },
      { text: "Components", link: "/component-list" },
    ],
    sidebar: [
      {
        text: "Guide",
        items: [
          { text: "Getting started", link: "/getting-started" },
          { text: "Builder basics", link: "/builder-basics" },
          { text: "Application state", link: "/application-state" },
          { text: "Event handlers", link: "/event-handlers" },
          { text: "Handling inputs", link: "/handling-inputs" },
        ],
      },
      {
        text: "Advanced",
        items: [
          { text: "Repeater", link: "/repeater" },
          {
            text: "Backend-initiated actions",
            link: "/backend-initiated-actions",
          },
          { text: "Page routes", link: "/page-routes" },
          { text: "Sessions", link: "/sessions" },
          { text: "Custom server", link: "/custom-server" },
        ],
      },
      {
        text: "Extending it",
        items: [
          {
            text: "Stylesheets",
            link: "/stylesheets",
          },
          {
            text: "Frontend scripts",
            link: "/frontend-scripts",
          },
          {
            text: "Custom components",
            link: "/custom-components",
          },
        ],
      },
      {
        text: "Reference",
        items: [
          { text: "Testing", link: "/testing" },
          { text: "Deploy with Docker", link: "/deploy-with-docker" },
          { text: "Component list", link: "/component-list" },
        ],
      },
    ],
  },
  vite: {
    build: {
      target: "esnext",
    },
  	define: {
		  STREAMSYNC_LIVE_CCT: JSON.stringify("no"),
    },
  },
};
