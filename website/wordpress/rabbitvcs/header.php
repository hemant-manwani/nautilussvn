<?php
/**
 * @package RabbitVCS
 * @subpackage Template
 */
?>
<?php echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" <?php language_attributes(); ?>>
    <head profile="http://gmpg.org/xfn/11">
        <meta http-equiv="Content-Type" content="<?php bloginfo('html_type'); ?>; charset=<?php bloginfo('charset'); ?>" />
        <title><?php wp_title('&laquo;', true, 'right'); ?> <?php bloginfo('name'); ?></title>
        <link rel="stylesheet" href="<?php bloginfo('stylesheet_url'); ?>" type="text/css" media="screen" />
        <link rel="pingback" href="<?php bloginfo('pingback_url'); ?>" />
        <?php wp_head(); ?>
    </head>
    <body <?php body_class(); ?>>
        <div id="page">
            <div id="page-head">
                <div id="page-logo">
                    <h1><a href="<?php echo get_option('home'); ?>/"><?php bloginfo('name'); ?></a></h1>
                </div>
                
                <div id="page-locationbar">
                    <ul>
                        <li id="link-home"><a href="<?php echo get_option('home'); ?>/">Home</a></li>
                        <li id="link-download"><a href="<?php echo get_option('siteurl'); ?>/download">Download</a></li>
                        <li id="link-about"><a href="<?php echo get_option('siteurl'); ?>/about">About</a></li>
                        <li id="link-blog"><a href="<?php echo get_option('siteurl'); ?>/blog">Blog</a></li>
                        <li id="link-contribute"><a href="<?php echo get_option('siteurl'); ?>/contribute">Contribute</a></li>
                        <li id="link-support"><a href="<?php echo get_option('siteurl'); ?>/support">Support</a></li>
                        <li id="link-wiki"><a href="<?php echo get_option('siteurl'); ?>/wiki">Wiki</a></li>
                    </ul>
                </div>
            </div>
            
            <div id="page-content">
            
