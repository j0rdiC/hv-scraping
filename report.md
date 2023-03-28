## Process

- Problems:

1. Tried using bs4 with requests library. It seems the websites are using a scraping blocker and this is the kind of response I am getting when making the request programatically:

```html
<!DOCTYPE html>
<html>
  <head>
    <meta content="text/html;charset=utf-8" http-equiv="Content-Type" />
    <title>Reservas - Hotel Las Gaviotas</title>
    <meta content="noindex" name="robots" />
    <link href="/engine.css" rel="stylesheet" type="text/css" />
    <link
      href="https://fonts.googleapis.com/css?family=Open+Sans"
      media="all"
      rel="stylesheet"
      type="text/css"
    />
  </head>
  <body class="bookingstep">
    <div id="header">
      <div id="logo">
        <a
          alt="Hotel Las Gaviotas"
          href="https://www.hotellasgaviotas.com/"
          title="Hotel Las Gaviotas"
        >
        </a>
      </div>
    </div>
    <div id="container">
      <div
        data-idhotel="100376436"
        data-lang="es"
        data-mirai-engine="mirai_be"
      ></div>
      <div
        data-idhotel="100376436"
        data-init="auto"
        data-lang="es"
        data-mirai-engine="mirai_tr"
      ></div>
      <div
        data-idhotel="100376436"
        data-lang="es"
        data-mirai-engine="mirai_rs"
      ></div>
      <script
        src="https://js.mirai.com/mirai-loader/mirai.loader.js"
        type="text/javascript"
      ></script>
    </div>
  </body>
</html>
```

- solution_1 (FAIL): Change the headers to mimic a browser.

- solution_2 (FAIL): Use a sessionizer in the requests library.

- solution_3: Try selenium which executes a real chromium browser in the background lets you interact with it as if it was a real user. Slower but more powerful.
