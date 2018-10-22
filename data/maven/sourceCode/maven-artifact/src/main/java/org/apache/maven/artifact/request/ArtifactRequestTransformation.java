package org.apache.maven.artifact.request;

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

import org.apache.maven.artifact.Artifact;
import org.apache.maven.artifact.repository.ArtifactRepository;

import java.util.Map;
import java.util.Set;

/**
 * @author <a href="mailto:jason@maven.org">Jason van Zyl</a>
 * @version $Id$
 */
public interface ArtifactRequestTransformation
{
    static String ROLE = ArtifactRequestTransformation.class.getName();

    /**
     * Take in a artifact and return the transformed artifact. If no
     * transformation has occured the original artifact is returned.
     *
     * @param artifact Artifact to be transformed.
     * @return The transformed Artifact
     */
    Artifact transform( Artifact artifact,
                        ArtifactRepository localRepository,
                        Set remoteRepositories,
                        Map parameters )
        throws Exception;
}