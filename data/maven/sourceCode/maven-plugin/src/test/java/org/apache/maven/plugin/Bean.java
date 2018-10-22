package org.apache.maven.plugin;

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

/**
 * @author <a href="mailto:jason@maven.org">Jason van Zyl</a>
 * @version $Id$
 */
public class Bean
    extends BeanPluginAdapter
{
    public Bean()
    {
        super( new TestPlugin() );
    }

    public void setName( String name )
    {
        addParameter( "name", name );
    }

    public void setArtifactId( String artifactId )
    {
        addParameter( "artifactId", artifactId );
    }

    public void setFoo( String foo )
    {
        addParameter( "foo", foo );
    }

    public boolean hasExecuted()
    {
        return ((TestPlugin)getPlugin()).hasExecuted();
    }
}