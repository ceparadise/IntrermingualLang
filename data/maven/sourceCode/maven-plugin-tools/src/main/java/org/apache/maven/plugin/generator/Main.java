package org.apache.maven.plugin.generator;

/*
 * Copyright 2001-2004 The Apache Software Foundation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import org.apache.maven.plugin.generator.jelly.JellyHarnessGenerator;

/**
 * @author <a href="mailto:jason@maven.org">Jason van Zyl</a>
 * @version $Id$
 */
public class Main
{
    public static void main( String[] args )
        throws Exception
    {
        if ( args.length != 4 )
        {
            System.err.println( "Usage: pluggy <mode> <source directory> <output directory> <pom>" );

            System.exit( 1 );
        }

        String mode = args[0];

        String sourceDirectory = args[1];

        String outputDirectory = args[2];

        String pom = args[3];

        AbstractGenerator generator = null;

        if ( mode.equals( "descriptor" ) )
        {
            generator = new PluginDescriptorGenerator();
        }
        else if ( mode.equals( "xdoc" ) )
        {
            generator = new PluginXdocGenerator();
        }
        else if ( mode.equals( "jelly" ) )
        {
            generator = new JellyHarnessGenerator();
        }
        else if ( mode.equals( "bean" ) )
        {
            generator = new BeanGenerator();
        }

        generator.execute( sourceDirectory, outputDirectory, pom );
    }
}