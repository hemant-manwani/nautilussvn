<?php
/**
 * Template Name: Frontpage
 * @package RabbitVCS
 * @subpackage Template
 */
 
get_header(); ?>

            <div id="page-banner">
                <div id="page-banner-screenshot">
                    <a href="<?php echo get_option('siteurl'); ?>/screenshots"><img src="<?php bloginfo('stylesheet_directory'); ?>/images/screenshots/screenshot-context-menu.png"/></a>
                </div>
                
                <div id="page-banner-text">
                    <p id="page-banner-title">Easy version control with RabbitVCS</p>
                    
                    <div id="page-banner-body">
                        <p class="description">
                            RabbitVCS is a project with the goal of developing a collection of utilities to allow for better client integration with some of the popular version control systems. 
                        </p>
                    
                        <div id="page-banner-download">
                            <a href="<?php echo get_option('siteurl'); ?>/download"><img src="<?php bloginfo('stylesheet_directory'); ?>/images/download-button.png" alt="Download RabbitVCS" title="Download RabbitVCS"/></a>
                            <a href="<?php echo get_option('siteurl'); ?>/download#ubuntu"><img src="<?php bloginfo('stylesheet_directory'); ?>/images/systems/ubuntu.png" alt="Ubuntu" title="Ubuntu"/></a>
                            <a href="<?php echo get_option('siteurl'); ?>/download#debian"><img src="<?php bloginfo('stylesheet_directory'); ?>/images/systems/debian.png" alt="Debian" title="Debian"/></a>
                            <a href="<?php echo get_option('siteurl'); ?>/download#fedora"><img src="<?php bloginfo('stylesheet_directory'); ?>/images/systems/fedora.png" alt="Fedora" title="Fedora"/></a>
                            <a href="<?php echo get_option('siteurl'); ?>/download#suse"><img src="<?php bloginfo('stylesheet_directory'); ?>/images/systems/suse.png" alt="SUSE" title="SUSE"/></a>
                            <a href="<?php echo get_option('siteurl'); ?>/download#arch"><img src="<?php bloginfo('stylesheet_directory'); ?>/images/systems/arch.png" alt="Arch" title="Arch"/></a>
                            <a href="<?php echo get_option('siteurl'); ?>/download#gentoo"><img src="<?php bloginfo('stylesheet_directory'); ?>/images/systems/gentoo.png" alt="Gentoo" title="Gentoo"/></a>
                            <a href="<?php echo get_option('siteurl'); ?>/download#linux"><img src="<?php bloginfo('stylesheet_directory'); ?>/images/systems/linux.png" alt="Linux" title="Linux"/></a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="page-content">
                <div class="column column1">
                    <h2>Features</h2>
                </div>
                
                <div class="column column2">
                    <h2>From the Blog</h2>
                    <p>&nbsp;</p>
                    
                    <p class="more"><a href="<?php echo get_option('siteurl'); ?>/blog">more...</a></p>
                    
                    <h2>Project Activity</h2>
                    <p>&nbsp;</p>
                    
                    <p class="more"><a href="<?php echo get_option('siteurl'); ?>/activity">more...</a></p>
                </div>
                
                <div class="column column3">
                    <h2>Quick Links</h2>
                    <ul>
                        <li><a href="<?php echo get_option('siteurl'); ?>/screenshots">Screenshots</a></li>
                        <li><a href="<?php echo get_option('siteurl'); ?>/knownissues">Known Issues</a></li>
                        <li><a href="<?php echo get_option('siteurl'); ?>/roadmap">Roadmap</a></li>
                        <li><a href="<?php echo get_option('siteurl'); ?>/faq">FAQ</a></li>
                        <li><a href="<?php echo get_option('siteurl'); ?>/issues">Browse Source</a></li>
                        <li><a href="<?php echo get_option('siteurl'); ?>/issues">View Issues</a></li>
                    </ul>
                </div>
            </div>

<?php get_footer(); ?>
