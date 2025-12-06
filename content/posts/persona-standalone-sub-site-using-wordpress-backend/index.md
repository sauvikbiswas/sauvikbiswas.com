---
title: "Persona: Standalone sub-site using Wordpress backend"
date: 2020-07-09
categories: 
  - "coding"
tags: 
  - "persona"
  - "php"
  - "wordpress"
coverImage: "fe87e8be-73bf-4805-9435-b65e1ebb82ab-jokers-two-sides.jpg"
---

The genesis of this project came from my desire to publish my writings separately. I wanted it to be detached from the blog with its own look and feel but I did not want to have a separate content management system. I have been using Wordpress for quite some time and I am familiar with the content management backend—the composer, the media library, the settings, etc. I wanted to use the same system to publish my work but did not want these works to be visible in the blog itself.

**TL;DR:**  
The sub-site is available here: [http://sauvikbiswas.com/works/](http://sauvikbiswas.com/works/)  
The source code is available here: [https://github.com/sauvikbiswas/persona](https://github.com/sauvikbiswas/persona)

Fortunately, there was a workaround. I could publish these as pages and not link the pages to any menu. That way, unless I share the permalink of the page, there was no way that anyone could ever find it out on their own.

{{< figure src="Screen-Shot-2020-07-09-at-10.38.11-PM-1024x513.png" caption="This is how a page looks on my site. This text is accessible from the unlisted URL." >}}

After I had written a couple of poems (and I have the desire to publish some essays and other standalone pieces of work in the future), I wanted to segregate them. One way would be to prepare another page with links of all these unlisted pages and place them on my site. Since I wanted to use a different look and feel, I had to decouple the sub-page from the Wordpress rendering engine—or, more aptly, generate a sub-site. In order to do this, I had to take a slightly different route.

The first hurdle was to classify these pages using some sort of taxonomy. Fortunately, Wordpress supports categories and tags. Unfortunately, they are not natively available to the pages. Since posts and pages are both stored in the same table—wp-posts, I knew that it was doable. After digging around, I found a plugin that does exactly that. It's called "Post Tags and Categories for Pages" \[[https://wordpress.org/plugins/post-tags-and-categories-for-pages/](https://wordpress.org/plugins/post-tags-and-categories-for-pages/)\]. This particular one is slightly outdated but does the job. There are a couple of other plugins that can do the same.

{{< figure src="Screen-Shot-2020-07-09-at-10.48.15-PM.png" caption="The Categories and Tags option is enabled here. The page editor now supports addition of both categories and tags." >}}

The next step was to run a direct SQL query in the Wordpress database and filter pages based on a chosen category. During composition, I used "works" as a category (specifically, as a slug) and used tags like "poetry" or "essay" for labelling the nature of the work.

The taxonomy storage and relationship is not so straightforward. Fortunately, Wordpress codex has a nice diagram that explains much of the relationships and has some documentation regarding the various fields of the tables in the database. Also, I must mention that it is easy to fetch the database credentials directly from the wp-config.php file present in the default installation of Wordpress in order to access the database. That way the shared project code remains secure.

{{< figure src="WP4.4.2-ERD-726x1024.png" caption="[https://codex.wordpress.org/Database\_Description](https://codex.wordpress.org/Database_Description)" >}}

Here is the code that fetches a page based on the permalink. The page has to be classified as that category (the "slug" in wp\_terms table) in order to get a non-null output.

```
<?php
function get_page_by_post_name($conn_ptr, $table_prefix, $post_name) {
    $sql="SELECT p.* FROM ".$table_prefix."posts p 
        INNER JOIN ".$table_prefix."term_relationships r ON r.object_id=p.ID 
            INNER JOIN ".$table_prefix."term_taxonomy t ON t.term_taxonomy_id = r.term_taxonomy_id 
            INNER JOIN ".$table_prefix."terms wt on wt.term_id = t.term_id 
        WHERE t.taxonomy='category' AND wt.slug='" . $GLOBALS['site_persona'] . "' AND p.post_type='page' AND p.post_status='publish' AND p.post_name='".$post_name."'";

    $result = $conn_ptr->query($sql);
    if ($result->num_rows == 0) return NULL;
    else {
        $row = $result->fetch_assoc();
        return $row;
    }
}
?>

```

For the landing page listing, the aggregation needs two passes of SQL queries—the first one to fetch a list of all pages and the next pass to obtain a list of tags corresponding to the pages.

```
<?php
function get_post_list($conn_ptr, $table_prefix) {
    // Get a list of post_titles and  post_names and store them in an array
    $sql="SELECT p.ID, p.post_title, p.post_name, p.post_date, p.post_modified FROM ".$table_prefix."posts p 
        INNER JOIN ".$table_prefix."term_relationships r ON r.object_id=p.ID 
            INNER JOIN ".$table_prefix."term_taxonomy t ON t.term_taxonomy_id = r.term_taxonomy_id 
            INNER JOIN ".$table_prefix."terms wt on wt.term_id = t.term_id 
        WHERE t.taxonomy='category' AND wt.slug='" . $GLOBALS['site_persona'] . "' AND p.post_type='page' AND p.post_status='publish' ";

    $result = $conn_ptr->query($sql);
    $rows = [];
    if ($result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) 
        array_push($rows, $row);
    }

    // Enrich the array with tags
    $erows = [];
    foreach ($rows as $row) {
        $sql="SELECT wt.name, t.taxonomy FROM ".$table_prefix."posts p 
        INNER JOIN ".$table_prefix."term_relationships r ON r.object_id=p.ID 
            INNER JOIN ".$table_prefix."term_taxonomy t ON t.term_taxonomy_id = r.term_taxonomy_id 
            INNER JOIN ".$table_prefix."terms wt on wt.term_id = t.term_id 
        WHERE t.taxonomy='post_tag' AND p.ID='".$row["ID"]."'";
    
        $tags = [];
        $result = $conn_ptr->query($sql);
        if ($result->num_rows > 0) while ($wtrow = $result->fetch_assoc()) array_push($tags, $wtrow["name"]);
        $row["post_tags"]=$tags;
        array_push($erows, $row);
    }
    return $erows;
}
?>

```

With that out of the way, I could create a small set of variables (some of them are already used in composing the SQL queries) that can be configured by the user and segregate all the files for generating the actual sub-site into a subfolder. This subfolder is analogous to a theme.

```
<?php
$site_persona = "works"; // slug of the category for sub-site
$site_name = "Sauvik Biswas: Works";
$theme_folder = "theme";
$landing_file = "landing.php";
$page_file = "page.php";
?>

```

I realised that I would not need any more than two specific files to generate a landing page and an individual page. In fact, one can code the whole thing into a single file and set $page\_file = $landing\_file. These files and a couple of helper files are located in the theme folder.

{{< figure src="Screen-Shot-2020-07-09-at-11.29.43-PM-1024x292.png" caption="My current landing page" >}}

{{< figure src="Screen-Shot-2020-07-09-at-11.31.00-PM-1024x404.png" caption="This is my current individual page. This is the same data that was rendered on the unlisted page." >}}

```
persona |
. |index.php
. |theme
. |theme |landing.php
. |theme |page.php
. |theme |header.php
. |theme |footer.php
. |theme |style.css

```

The code can be found at [https://github.com/sauvikbiswas/persona](https://github.com/sauvikbiswas/persona)

As a postscript, I would ask the reader to visit the many sites administered by Kevin Kelly. His homepage is [https://kk.org/](https://kk.org/). He also has a couple of other sites like [https://truefilms.com/](https://truefilms.com/) and [https://asiagrace.com/](https://asiagrace.com/) as well as many sub-sites which probably use a lot of common code and possibly a single backend. Of course, there is no way I would know for sure but if I was in his place, I would try to tackle it in this fashion.
