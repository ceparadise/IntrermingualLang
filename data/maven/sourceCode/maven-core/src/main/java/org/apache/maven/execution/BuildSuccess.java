package org.apache.maven.execution;

/*
 * Copyright 2001-2005 The Apache Software Foundation.
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

import org.apache.maven.project.MavenProject;

/**
 * Describe a build success in the reactor.
 *
 * @author <a href="mailto:brett@apache.org">Brett Porter</a>
 * @version $Id$
 */
public class BuildSuccess
{
    private final MavenProject project;

    private final long time;

    public BuildSuccess( MavenProject project, long time )
    {
        this.project = project;
        this.time = time;
    }

    public MavenProject getProject()
    {
        return project;
    }

    public long getTime()
    {
        return time;
    }
}
