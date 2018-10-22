package org.apache.maven.artifact.repository.metadata;

/*
 * Copyright 2005 The Apache Software Foundation.
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

public class GroupRepositoryMetadata
    implements RepositoryMetadata
{
    /**
     * TODO: reuse.
     */
    protected static final String METADATA_FILE = "maven-metadata.xml";

    private final String groupId;

    public GroupRepositoryMetadata( String groupId )
    {
        this.groupId = groupId;
    }

    public String getRepositoryPath()
    {
        return groupId + "/" + METADATA_FILE;
    }

    public String toString()
    {
        return "repository metadata for group: \'" + groupId + "\'";
    }

}
